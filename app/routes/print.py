"""Print-ready PDF export: interior, cover, preview, certificate."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.config import settings
from app.database import get_db
from app.models import Account, Book, BookChapter, Document, DocumentVersion
from app.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/books", tags=["print"])


def _require_pro(account: Account):
    if (account.tier or "free") != "pro":
        raise HTTPException(status_code=403, detail="Print export requires a Pro subscription")


async def _load_book_with_chapters(book_id: str, account_id, db: AsyncSession):
    """Load book, verify ownership, return (book, chapters_data)."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.deleted_at:
        raise HTTPException(status_code=410, detail="Book has been deleted")
    if book.account_id != account_id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id).order_by(BookChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()

    chapters_data = []
    for ch in chapters:
        doc_result = await db.execute(
            select(Document).where(Document.id == ch.document_id, Document.deleted_at.is_(None))
        )
        doc = doc_result.scalar_one_or_none()
        if not doc:
            continue
        ver_result = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == doc.id,
                DocumentVersion.version == doc.current_version,
            )
        )
        ver = ver_result.scalar_one_or_none()
        if not ver:
            continue
        chapters_data.append({
            "chapter_number": ch.chapter_number,
            "title": doc.title or ch.chapter_title,
            "content": ver.content,
            "rendered_html": ver.rendered_html or "",
        })

    if not chapters_data:
        raise HTTPException(status_code=422, detail="Book has no chapters")

    return book, chapters_data


@router.post("/{book_id}/print/preview")
@limiter.limit("10/hour")
async def print_preview(
    book_id: str,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Generate a 10-page preview PDF of the interior."""
    book, chapters_data = await _load_book_with_chapters(book_id, auth.account.id, db)

    from app.services.print_pdf import generate_interior_pdf, generate_preview_pdf

    full_pdf = await generate_interior_pdf(
        book_title=book.title,
        subtitle=book.subtitle,
        authors=book.authors or [],
        chapters=chapters_data,
        license_key=book.license or "all-rights-reserved",
        pub_date=book.created_at,
    )
    preview_pdf = await generate_preview_pdf(full_pdf, max_pages=10)

    filename = f"{book.slug or book.id}-preview.pdf"
    return Response(
        content=preview_pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{book_id}/print/interior")
@limiter.limit("5/hour")
async def print_interior(
    book_id: str,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Generate full print-ready interior PDF (6"x9" trade paperback). Pro required."""
    _require_pro(auth.account)
    book, chapters_data = await _load_book_with_chapters(book_id, auth.account.id, db)

    from app.services.print_pdf import generate_interior_pdf

    pdf = await generate_interior_pdf(
        book_title=book.title,
        subtitle=book.subtitle,
        authors=book.authors or [],
        chapters=chapters_data,
        license_key=book.license or "all-rights-reserved",
        pub_date=book.created_at,
    )

    filename = f"{book.slug or book.id}-interior.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{book_id}/print/cover")
@limiter.limit("10/hour")
async def print_cover(
    book_id: str,
    request: Request,
    page_count: int = 200,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Generate print-ready cover PDF (300 DPI with bleed). Pro required.

    Pass `page_count` query param to set spine width (default 200).
    """
    _require_pro(auth.account)

    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.deleted_at:
        raise HTTPException(status_code=410, detail="Book has been deleted")
    if book.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    author_name = book.authors[0]["name"] if book.authors else None

    from app.services.print_cover import generate_cover_pdf

    pdf = await generate_cover_pdf(
        title=book.title,
        subtitle=book.subtitle,
        author_name=author_name,
        description=book.description,
        page_count=page_count,
    )

    filename = f"{book.slug or book.id}-cover.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{book_id}/print/certificate")
@limiter.limit("30/hour")
async def print_certificate(
    book_id: str,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Generate Certificate of Publication PDF. Free for all users."""
    book, chapters_data = await _load_book_with_chapters(book_id, auth.account.id, db)

    from app.services.print_pdf import _compute_book_hash, generate_certificate_pdf

    content_hash = _compute_book_hash(chapters_data)
    permanent_url = f"{settings.base_url}/{book.slug}" if book.slug else f"{settings.base_url}/books/{book.id}"

    pdf = await generate_certificate_pdf(
        book_title=book.title,
        authors=book.authors or [],
        pub_date=book.created_at,
        content_hash=content_hash,
        license_key=book.license or "all-rights-reserved",
        permanent_url=permanent_url,
    )

    filename = f"{book.slug or book.id}-certificate.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
