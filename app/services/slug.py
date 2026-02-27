"""Slug generation + uniqueness enforcement."""

import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document


def generate_slug(title: str) -> str:
    """Generate a URL slug from a title."""
    # Unicode normalize
    slug = unicodedata.normalize("NFKD", title)
    # Remove non-ASCII
    slug = slug.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    slug = slug.lower()
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    # Max 80 chars
    if len(slug) > 80:
        slug = slug[:80].rstrip("-")
    return slug or "untitled"


async def ensure_unique_slug(slug: str, db: AsyncSession, exclude_doc_id: str | None = None) -> str:
    """Ensure slug is unique, appending -2, -3, etc. if needed."""
    candidate = slug
    counter = 2
    while True:
        query = select(Document.id).where(
            Document.slug == candidate,
            Document.deleted_at.is_(None),
        )
        if exclude_doc_id:
            query = query.where(Document.id != exclude_doc_id)
        result = await db.execute(query)
        if result.scalar_one_or_none() is None:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1
