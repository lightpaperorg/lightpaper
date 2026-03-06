"""Slug generation + uniqueness enforcement."""

import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book, Document

# Platform-reserved slugs — cannot be claimed by documents
RESERVED_SLUGS = frozenset(
    {
        "about",
        "admin",
        "api",
        "app",
        "auth",
        "blog",
        "billing",
        "changelog",
        "community",
        "contact",
        "dashboard",
        "docs",
        "download",
        "explore",
        "faq",
        "features",
        "feedback",
        "guidelines",
        "help",
        "home",
        "index",
        "invite",
        "jobs",
        "legal",
        "login",
        "logout",
        "mcp",
        "new",
        "newsletter",
        "notifications",
        "null",
        "onboarding",
        "org",
        "plans",
        "pricing",
        "privacy",
        "pro",
        "profile",
        "register",
        "reports",
        "search",
        "security",
        "settings",
        "signup",
        "sitemap",
        "status",
        "support",
        "team",
        "terms",
        "topics",
        "trending",
        "undefined",
        "unsubscribe",
        "upload",
        "user",
        "users",
        "verify",
        "webhooks",
        "welcome",
        "books",
        "wiki",
    }
)


def is_reserved_slug(slug: str) -> bool:
    """Check if a slug is reserved by the platform."""
    return slug.lower().strip("-") in RESERVED_SLUGS


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
    slug = slug or "untitled"
    # Auto-suffix reserved slugs when auto-generated from title
    if is_reserved_slug(slug):
        slug = f"{slug}-doc"
    return slug


async def ensure_unique_slug(slug: str, db: AsyncSession, exclude_doc_id: str | None = None) -> str:
    """Ensure slug is unique across documents and books, appending -2, -3, etc. if needed."""
    candidate = slug
    counter = 2
    while True:
        # Check documents
        doc_query = select(Document.id).where(
            Document.slug == candidate,
            Document.deleted_at.is_(None),
        )
        if exclude_doc_id:
            doc_query = doc_query.where(Document.id != exclude_doc_id)
        doc_result = await db.execute(doc_query)
        # Check books
        book_query = select(Book.id).where(
            Book.slug == candidate,
            Book.deleted_at.is_(None),
        )
        book_result = await db.execute(book_query)
        if doc_result.scalar_one_or_none() is None and book_result.scalar_one_or_none() is None:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


async def ensure_unique_book_slug(slug: str, db: AsyncSession, exclude_book_id: str | None = None) -> str:
    """Ensure book slug is unique across both books and documents."""
    candidate = slug
    counter = 2
    while True:
        # Check books
        book_query = select(Book.id).where(
            Book.slug == candidate,
            Book.deleted_at.is_(None),
        )
        if exclude_book_id:
            book_query = book_query.where(Book.id != exclude_book_id)
        book_result = await db.execute(book_query)
        # Check documents
        doc_query = select(Document.id).where(
            Document.slug == candidate,
            Document.deleted_at.is_(None),
        )
        doc_result = await db.execute(doc_query)
        if book_result.scalar_one_or_none() is None and doc_result.scalar_one_or_none() is None:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1
