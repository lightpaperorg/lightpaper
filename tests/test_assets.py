"""Unit tests for the image/asset pipeline (pure logic — no DB or GCS needed)."""

import base64
import io

import pytest
from PIL import Image

from app.services import assets as A


def _png_bytes(w=20, h=10, color=(200, 180, 120)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), color).save(buf, format="PNG")
    return buf.getvalue()


def test_inspect_png():
    ext, ct, w, h = A._inspect(_png_bytes(20, 10))
    assert ext == "png"
    assert ct == "image/png"
    assert (w, h) == (20, 10)


def test_inspect_rejects_non_image():
    with pytest.raises(A.AssetError):
        A._inspect(b"this is not an image")


def test_decode_base64_plain_and_datauri():
    raw = _png_bytes()
    b64 = base64.b64encode(raw).decode()
    assert A.decode_base64_image(b64) == raw
    assert A.decode_base64_image(f"data:image/png;base64,{b64}") == raw


def test_decode_base64_invalid():
    with pytest.raises(A.AssetError):
        A.decode_base64_image("!!!not base64!!!")


def test_public_url():
    from app.config import settings

    assert A.public_url("a" * 64, "png") == f"{settings.base_url}/i/{'a' * 64}.png"


def test_asset_key_regex():
    assert A.ASSET_KEY_RE.match("f" * 64 + ".png")
    assert A.ASSET_KEY_RE.match("0" * 64 + ".webp")
    assert not A.ASSET_KEY_RE.match("short.png")
    assert not A.ASSET_KEY_RE.match("g" * 64 + ".png")  # 'g' not hex
    assert not A.ASSET_KEY_RE.match("../secret.png")  # no traversal
    assert not A.ASSET_KEY_RE.match("f" * 64 + ".svg")  # svg not allowed


def test_content_type_for_key():
    assert A.content_type_for_key("abc.jpg") == "image/jpeg"
    assert A.content_type_for_key("abc.webp") == "image/webp"


def test_rewrite_asset_refs_basic():
    content = "See ![Cost chart](asset:chart1) and ![Jobs](asset:jobs_2)."
    out = A.rewrite_asset_refs(
        content, {"chart1": "https://lightpaper.org/i/aa.png", "jobs_2": "https://lightpaper.org/i/bb.png"}
    )
    assert "https://lightpaper.org/i/aa.png" in out
    assert "https://lightpaper.org/i/bb.png" in out
    assert "asset:" not in out


def test_rewrite_leaves_unknown_untouched():
    content = "![x](asset:missing)"
    assert A.rewrite_asset_refs(content, {"other": "https://x/y.png"}) == content


def test_rewrite_empty_map_noop():
    content = "![x](asset:chart1)"
    assert A.rewrite_asset_refs(content, {}) == content


def test_schema_publish_accepts_assets():
    from app.schemas import PublishRequest

    req = PublishRequest(
        title="T",
        content="# H\n\nbody ![c](asset:chart1)",
        assets=[{"name": "chart1", "data": base64.b64encode(_png_bytes()).decode()}],
    )
    assert req.assets[0].name == "chart1"
