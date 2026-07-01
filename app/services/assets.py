"""Image/asset storage: validate → content-address (SHA-256) → GCS → on-domain URL.

Assets are served on-domain at /i/{sha256}.{ext} (see app/routes/assets.py), so the
GCS bucket can stay private. Content-addressing means identical images are stored and
served once, and their URLs are immutable and safe to cache forever.
"""

import asyncio
import base64
import hashlib
import io
import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Asset

# Pillow is already a dependency (OG images, print cover). We use it to validate
# that the bytes really are an image and to read the true format + dimensions,
# rather than trusting a caller-supplied content-type.
from PIL import Image

# Canonical, safe raster formats. SVG is intentionally excluded (script/XSS risk).
_FORMAT_TO_EXT = {"PNG": "png", "JPEG": "jpg", "GIF": "gif", "WEBP": "webp"}
_FORMAT_TO_CT = {"PNG": "image/png", "JPEG": "image/jpeg", "GIF": "image/gif", "WEBP": "image/webp"}
_EXT_TO_CT = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}

# A served asset key looks like "<64 hex sha>.<ext>" — validated before touching storage.
ASSET_KEY_RE = re.compile(r"^[0-9a-f]{64}\.(png|jpg|jpeg|gif|webp)$")

# Reference tokens inside markdown: ![alt](asset:chart1) or <img src="asset:chart1">
_ASSET_REF_RE = re.compile(r"asset:([A-Za-z0-9._-]+)")

# Names authors give inline assets in a publish payload.
ASSET_NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


class AssetError(ValueError):
    """Raised for invalid/oversized/unsupported image input."""


@dataclass
class AssetRef:
    id: str  # the content hash — also the stable public identifier
    url: str
    content_type: str
    bytes: int
    width: int
    height: int


def _inspect(data: bytes) -> tuple[str, str, int, int]:
    """Return (ext, content_type, width, height) or raise AssetError."""
    try:
        with Image.open(io.BytesIO(data)) as im:
            fmt = im.format
            width, height = im.size
    except Exception as exc:  # noqa: BLE001 — any decode failure means "not a valid image"
        raise AssetError("Could not read the file as an image.") from exc
    if fmt not in _FORMAT_TO_EXT:
        raise AssetError(f"Unsupported image format {fmt!r}. Use PNG, JPEG, GIF, or WEBP.")
    return _FORMAT_TO_EXT[fmt], _FORMAT_TO_CT[fmt], int(width), int(height)


def public_url(sha256: str, ext: str) -> str:
    return f"{settings.base_url}/i/{sha256}.{ext}"


def content_type_for_key(key: str) -> str:
    ext = key.rsplit(".", 1)[-1].lower()
    return _EXT_TO_CT.get(ext, "application/octet-stream")


# --- GCS (blocking; always called via asyncio.to_thread) ---------------------


def _gcs_upload_if_absent(bucket: str, path: str, data: bytes, content_type: str) -> None:
    from google.cloud import storage as gcs

    client = gcs.Client()
    blob = client.bucket(bucket).blob(path)
    if blob.exists():  # content-addressed → identical bytes already stored
        return
    blob.cache_control = "public, max-age=31536000, immutable"
    blob.upload_from_string(data, content_type=content_type)


def _gcs_download(bucket: str, path: str) -> bytes | None:
    from google.cloud import storage as gcs

    client = gcs.Client()
    blob = client.bucket(bucket).blob(path)
    if not blob.exists():
        return None
    return blob.download_as_bytes()


# --- Public API --------------------------------------------------------------


async def store_asset(db: AsyncSession, account_id, data: bytes) -> AssetRef:
    """Validate, content-address, upload (if new), record, and return a reference.

    Does not commit — the caller's transaction owns the lifecycle. The GCS object
    is written immediately (idempotent by content), so a rolled-back DB row only
    leaves a harmless, reusable orphan object.
    """
    if not data:
        raise AssetError("Empty file.")
    if len(data) > settings.assets_max_bytes:
        mb = settings.assets_max_bytes // (1024 * 1024)
        raise AssetError(f"Image is too large. Maximum size is {mb}MB.")

    ext, content_type, width, height = _inspect(data)
    sha = hashlib.sha256(data).hexdigest()
    path = f"assets/{sha}.{ext}"

    await asyncio.to_thread(_gcs_upload_if_absent, settings.gcs_assets_bucket, path, data, content_type)

    # Best-effort DB record (dedup by content hash). Use a savepoint so a race on
    # the unique sha256 can't poison the caller's outer transaction.
    existing = (await db.execute(select(Asset).where(Asset.sha256 == sha))).scalar_one_or_none()
    if existing is None:
        try:
            async with db.begin_nested():
                db.add(
                    Asset(
                        account_id=account_id,
                        sha256=sha,
                        ext=ext,
                        content_type=content_type,
                        bytes=len(data),
                        width=width,
                        height=height,
                    )
                )
        except Exception:  # noqa: BLE001 — concurrent insert of the same content; fine
            pass

    return AssetRef(
        id=sha,
        url=public_url(sha, ext),
        content_type=content_type,
        bytes=len(data),
        width=width,
        height=height,
    )


def decode_base64_image(data_b64: str) -> bytes:
    """Decode a base64 image payload, tolerating a data: URI prefix."""
    s = data_b64.strip()
    if s.startswith("data:"):
        _, _, s = s.partition(",")
    try:
        return base64.b64decode(s, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise AssetError("Invalid base64 image data.") from exc


async def store_inline_assets(db: AsyncSession, account_id, assets) -> dict[str, str]:
    """Store a list of inline assets (name + base64 data); return {name: url}."""
    url_map: dict[str, str] = {}
    for a in assets:
        if not ASSET_NAME_RE.match(a.name):
            raise AssetError(f"Invalid asset name {a.name!r}. Use letters, digits, dot, dash, underscore.")
        ref = await store_asset(db, account_id, decode_base64_image(a.data))
        url_map[a.name] = ref.url
    return url_map


def rewrite_asset_refs(content: str, url_map: dict[str, str]) -> str:
    """Replace `asset:<name>` tokens in markdown with their hosted URLs.

    Unknown names are left untouched; the HTML sanitizer will drop them safely
    (non-http scheme), so a typo can never inject anything.
    """
    if not url_map:
        return content
    return _ASSET_REF_RE.sub(lambda m: url_map.get(m.group(1), m.group(0)), content)


async def process_inline_assets(db: AsyncSession, account_id, content: str, assets) -> str:
    """Store inline assets and rewrite their references in `content`."""
    if not assets:
        return content
    return rewrite_asset_refs(content, await store_inline_assets(db, account_id, assets))


async def load_asset_bytes(key: str) -> tuple[bytes, str] | None:
    """For the serving route: return (bytes, content_type) for a validated key, or None."""
    if not ASSET_KEY_RE.match(key):
        return None
    data = await asyncio.to_thread(_gcs_download, settings.gcs_assets_bucket, f"assets/{key}")
    if data is None:
        return None
    return data, content_type_for_key(key)
