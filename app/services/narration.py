"""ElevenLabs Studio narration service: markdown→plaintext, project creation, GCS upload."""

import logging
import re
import secrets

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Book, BookChapter, Document, DocumentVersion, Narration, NarrationChapter

logger = logging.getLogger(__name__)

ELEVENLABS_API = "https://api.elevenlabs.io"

# Curated voice list — ElevenLabs premade voices good for narration
VOICES = [
    {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "description": "Deep, warm male voice. Great for non-fiction and technical content.", "preview_url": None},
    {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "description": "Well-rounded male voice with clear enunciation. Versatile narrator.", "preview_url": None},
    {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "description": "Soft, warm female voice. Ideal for fiction and memoir.", "preview_url": None},
    {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "description": "Young, energetic female voice. Good for YA and tutorials.", "preview_url": None},
    {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "description": "Young, conversational male voice. Good for casual non-fiction.", "preview_url": None},
    {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "description": "Authoritative, deep male voice. Suits business and leadership content.", "preview_url": None},
    {"voice_id": "pqHfZKP75CvOlQylNhV4", "name": "Bill", "description": "Calm, measured male voice. Well-suited for essays and long reads.", "preview_url": None},
    {"voice_id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "description": "British male voice. Refined, clear narration style.", "preview_url": None},
    {"voice_id": "XB0fDUnXU5powFXDhCwa", "name": "Charlotte", "description": "Elegant female voice with warmth. Great for literary fiction.", "preview_url": None},
    {"voice_id": "Xb7hH8MSUJpSbSDYk0k2", "name": "Alice", "description": "Friendly, articulate female voice. Good all-around narrator.", "preview_url": None},
]


def markdown_to_plain_text(content: str) -> str:
    """Strip markdown formatting to produce clean text for TTS narration."""
    text = content

    # Remove code blocks (fenced and indented)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"(?m)^    .+$", "", text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

    # Convert links to just text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove footnote references
    text = re.sub(r"\[\^[^\]]+\]", "", text)

    # Remove footnote definitions
    text = re.sub(r"(?m)^\[\^[^\]]+\]:.*$", "", text)

    # Remove headings markers but keep text
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)

    # Remove bold/italic markers
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)

    # Remove inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove strikethrough
    text = re.sub(r"~~([^~]+)~~", r"\1", text)

    # Remove blockquote markers
    text = re.sub(r"(?m)^>\s?", "", text)

    # Remove horizontal rules
    text = re.sub(r"(?m)^[-*_]{3,}\s*$", "", text)

    # Remove list markers
    text = re.sub(r"(?m)^[\s]*[-*+]\s+", "", text)
    text = re.sub(r"(?m)^[\s]*\d+\.\s+", "", text)

    # Remove table formatting
    text = re.sub(r"(?m)^\|.*\|$", "", text)
    text = re.sub(r"(?m)^[-:|]+$", "", text)

    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def generate_narration_id() -> str:
    return f"nar_{secrets.token_hex(8)}"


def generate_callback_token() -> str:
    return secrets.token_hex(32)


async def estimate_narration(book_id: str, db: AsyncSession, max_chapters: int | None = None) -> dict:
    """Estimate narration cost for a book. Returns character counts and price."""
    book_result = await db.execute(
        select(Book).where(Book.id == book_id, Book.deleted_at.is_(None))
    )
    book = book_result.scalar_one_or_none()
    if not book:
        raise ValueError("Book not found")

    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book_id).order_by(BookChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()
    if not chapters:
        raise ValueError("Book has no chapters")

    if max_chapters:
        chapters = chapters[:max_chapters]

    chapter_estimates = []
    total_chars = 0

    for ch in chapters:
        ver_result = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == ch.document_id,
                DocumentVersion.version == (
                    select(Document.current_version).where(Document.id == ch.document_id).scalar_subquery()
                ),
            )
        )
        version = ver_result.scalar_one_or_none()
        if not version:
            continue

        plain_text = markdown_to_plain_text(version.content)
        char_count = len(plain_text)
        total_chars += char_count

        chapter_estimates.append({
            "chapter_number": ch.chapter_number,
            "document_id": ch.document_id,
            "title": ch.chapter_title,
            "character_count": char_count,
        })

    cost_per_char = settings.narration_cost_per_char
    price_cents = max(100, int(total_chars * cost_per_char * 100))  # minimum $1

    return {
        "book_id": book_id,
        "book_title": book.title,
        "total_characters": total_chars,
        "price_cents": price_cents,
        "price_display": f"${price_cents / 100:.2f}",
        "chapters": chapter_estimates,
    }


async def start_narration(narration_id: str, db: AsyncSession) -> None:
    """Create an ElevenLabs Studio project and start conversion."""
    narration_result = await db.execute(
        select(Narration).where(Narration.id == narration_id)
    )
    narration = narration_result.scalar_one_or_none()
    if not narration:
        logger.error("Narration %s not found", narration_id)
        return

    # Load chapters
    chapters_result = await db.execute(
        select(NarrationChapter).where(NarrationChapter.narration_id == narration_id)
        .order_by(NarrationChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()

    # Build content JSON for ElevenLabs Studio
    content_parts = []
    for ch in chapters:
        ver_result = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == ch.document_id,
                DocumentVersion.version == (
                    select(Document.current_version).where(Document.id == ch.document_id).scalar_subquery()
                ),
            )
        )
        version = ver_result.scalar_one_or_none()
        if not version:
            continue

        plain_text = markdown_to_plain_text(version.content)
        content_parts.append({
            "title": f"Chapter {ch.chapter_number}",
            "content": plain_text,
        })

    callback_url = f"{settings.base_url}/v1/narration/callback/{narration.callback_token}"

    try:
        import json as _json

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{ELEVENLABS_API}/v1/studio/projects",
                headers={
                    "xi-api-key": settings.elevenlabs_api_key,
                },
                data={
                    "name": f"lightpaper-{narration_id}",
                    "from_content_json": _json.dumps(content_parts),
                    "default_voice_id": narration.voice_id,
                    "quality_preset": "high",
                    "auto_convert": "true",
                    "callback_url": callback_url,
                },
            )

            if resp.status_code not in (200, 201):
                error_text = resp.text[:500]
                logger.error("ElevenLabs project creation failed: %s %s", resp.status_code, error_text)
                await db.execute(
                    update(Narration).where(Narration.id == narration_id)
                    .values(status="failed", error_message=f"ElevenLabs API error: {error_text}")
                )
                await db.commit()
                return

            project_data = resp.json()
            project_id = project_data.get("project_id") or project_data.get("id")

            # Update narration with project ID
            await db.execute(
                update(Narration).where(Narration.id == narration_id)
                .values(
                    elevenlabs_project_id=project_id,
                    status="converting",
                )
            )

            # Update chapter IDs if available
            chapters_data = project_data.get("chapters", [])
            for i, ch_data in enumerate(chapters_data):
                if i < len(chapters):
                    await db.execute(
                        update(NarrationChapter).where(NarrationChapter.id == chapters[i].id)
                        .values(elevenlabs_chapter_id=ch_data.get("chapter_id") or ch_data.get("id"))
                    )

            await db.commit()
            logger.info("Narration %s: ElevenLabs project %s created, converting", narration_id, project_id)

    except Exception as e:
        logger.error("Failed to start narration %s: %s", narration_id, str(e))
        await db.execute(
            update(Narration).where(Narration.id == narration_id)
            .values(status="failed", error_message=str(e)[:500])
        )
        await db.commit()


async def handle_callback(callback_token: str, db: AsyncSession) -> bool:
    """Handle ElevenLabs completion callback: download audio, upload to GCS."""
    narration_result = await db.execute(
        select(Narration).where(Narration.callback_token == callback_token)
    )
    narration = narration_result.scalar_one_or_none()
    if not narration:
        logger.warning("Callback with unknown token")
        return False

    if not narration.elevenlabs_project_id:
        logger.error("Narration %s has no project ID", narration.id)
        return False

    chapters_result = await db.execute(
        select(NarrationChapter).where(NarrationChapter.narration_id == narration.id)
        .order_by(NarrationChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()

    bucket = narration.gcs_bucket or settings.gcs_audio_bucket

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            # Get project snapshots to find the latest conversion
            snap_resp = await client.get(
                f"{ELEVENLABS_API}/v1/studio/projects/{narration.elevenlabs_project_id}/snapshots",
                headers={"xi-api-key": settings.elevenlabs_api_key},
            )
            if snap_resp.status_code != 200:
                raise Exception(f"Failed to get snapshots: {snap_resp.status_code}")

            snapshots = snap_resp.json().get("snapshots", [])
            if not snapshots:
                raise Exception("No snapshots available")

            latest_snapshot = snapshots[0]
            snapshot_id = latest_snapshot.get("snapshot_id") or latest_snapshot.get("id")

            # Download each chapter's audio
            for ch in chapters:
                chapter_id = ch.elevenlabs_chapter_id
                if not chapter_id:
                    # Try to get from snapshot chapters
                    continue

                audio_resp = await client.get(
                    f"{ELEVENLABS_API}/v1/studio/projects/{narration.elevenlabs_project_id}"
                    f"/snapshots/{snapshot_id}/stream",
                    headers={"xi-api-key": settings.elevenlabs_api_key},
                    params={"chapter_id": chapter_id},
                )

                if audio_resp.status_code != 200:
                    logger.warning("Failed to download chapter %s audio: %s", ch.chapter_number, audio_resp.status_code)
                    continue

                audio_data = audio_resp.content
                gcs_path = f"narrations/{narration.id}/ch{ch.chapter_number}.mp3"
                audio_url = await _upload_to_gcs(bucket, gcs_path, audio_data)

                # Estimate duration: MP3 at ~128kbps → bytes / 16000 ≈ seconds
                duration_estimate = len(audio_data) // 16000

                await db.execute(
                    update(NarrationChapter).where(NarrationChapter.id == ch.id)
                    .values(
                        audio_url=audio_url,
                        audio_duration_seconds=duration_estimate,
                        elevenlabs_snapshot_id=snapshot_id,
                        status="complete",
                    )
                )

        # Mark narration complete
        from datetime import datetime, timezone
        await db.execute(
            update(Narration).where(Narration.id == narration.id)
            .values(
                status="complete",
                audio_ready=True,
                gcs_bucket=bucket,
                completed_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
        logger.info("Narration %s complete — audio uploaded to GCS", narration.id)
        return True

    except Exception as e:
        logger.error("Callback handling failed for narration %s: %s", narration.id, str(e))
        await db.execute(
            update(Narration).where(Narration.id == narration.id)
            .values(status="failed", error_message=str(e)[:500])
        )
        await db.commit()
        return False


async def _upload_to_gcs(bucket: str, path: str, data: bytes) -> str:
    """Upload bytes to Google Cloud Storage and return the public URL."""
    from google.cloud import storage as gcs

    client = gcs.Client()
    bucket_obj = client.bucket(bucket)
    blob = bucket_obj.blob(path)
    blob.upload_from_string(data, content_type="audio/mpeg")
    return f"https://storage.googleapis.com/{bucket}/{path}"
