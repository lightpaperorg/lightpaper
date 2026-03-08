"""Book publishing routes: POST /v1/books, GET/PUT/DELETE /v1/books/{id}, chapter management."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.config import settings
from app.database import get_db
from app.id_gen import generate_book_id, generate_doc_id
from app.models import Book, BookChapter, Credential, Document, DocumentVersion
from app.rate_limit import limiter
from app.schemas import (
    AddChapterRequest,
    AuthorInfo,
    BookResponse,
    BookUpdateRequest,
    ChapterResponse,
    PublishBookRequest,
    PublishBookResponse,
    QualityBreakdown,
    ReorderChaptersRequest,
)
from app.services.gravity import compute_credential_points, get_gravity_badges, get_next_level_instructions
from app.services.quality import score_book_quality, score_quality
from app.services.renderer import (
    compute_content_hash,
    compute_reading_time,
    compute_word_count,
    extract_toc,
    render_markdown,
)
from app.services.slug import ensure_unique_book_slug, ensure_unique_slug, generate_slug, is_reserved_slug

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency
_indexnow = None


async def _notify_search_engines(urls: list[str]):
    global _indexnow
    if _indexnow is None:
        from app.routes.discovery import notify_indexnow

        _indexnow = notify_indexnow
    await _indexnow(urls)


router = APIRouter(prefix="/v1", tags=["books"])

MIN_CHAPTER_WORD_COUNT = 100


def _generate_chapter_slug(book_slug: str, chapter_number: int, chapter_title: str) -> str:
    """Generate chapter slug: {book-slug}-ch{N}-{title-slug}."""
    title_slug = generate_slug(chapter_title)
    # Trim title slug to fit within 80 chars total
    prefix = f"{book_slug}-ch{chapter_number}-"
    max_title_len = 80 - len(prefix)
    if max_title_len > 0 and len(title_slug) > max_title_len:
        title_slug = title_slug[:max_title_len].rstrip("-")
    return f"{prefix}{title_slug}"


def _chapter_response(chapter: BookChapter, doc: Document, version: DocumentVersion | None) -> ChapterResponse:
    return ChapterResponse(
        chapter_number=chapter.chapter_number,
        document_id=doc.id,
        title=chapter.chapter_title or doc.title,
        url=f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}",
        permanent_url=f"{settings.base_url}/d/{doc.id}",
        word_count=version.word_count if version else 0,
        reading_time_minutes=version.reading_time if version else 0,
        quality_score=doc.quality_score or 0,
    )


async def _get_book_or_404(book_id: str, db: AsyncSession) -> Book:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.deleted_at is not None:
        raise HTTPException(status_code=410, detail="Book has been deleted")
    return book


@router.post("/books", response_model=PublishBookResponse, status_code=201)
@limiter.limit("20/hour")
async def publish_book(
    body: PublishBookRequest,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Publish a complete book with all chapters at once."""
    account_id = auth.account.id
    gravity_level = auth.gravity_level

    # Generate book ID and slug
    book_id = generate_book_id()
    custom_slug = body.options.slug
    if custom_slug and is_reserved_slug(custom_slug):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"The slug '{custom_slug}' is reserved and cannot be used.",
        )
    book_slug = custom_slug or generate_slug(body.title)
    book_slug = await ensure_unique_book_slug(book_slug, db)

    # Validate and process each chapter
    chapter_qualities = []  # (word_count, QualityResult)
    chapter_data = []  # processed chapter info
    total_word_count = 0
    all_urls = []

    for i, ch in enumerate(body.chapters, 1):
        word_count = compute_word_count(ch.content)
        if word_count < MIN_CHAPTER_WORD_COUNT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Chapter {i} ('{ch.title}') must be at least {MIN_CHAPTER_WORD_COUNT} words (got {word_count})",
            )

        if not any(line.strip().startswith("#") for line in ch.content.split("\n")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Chapter {i} ('{ch.title}') must contain at least one heading",
            )

        # Generate chapter document
        doc_id = generate_doc_id()
        chapter_slug = ch.slug or _generate_chapter_slug(book_slug, i, ch.title)
        chapter_slug = await ensure_unique_slug(chapter_slug, db)

        quality = score_quality(ch.title, ch.content)
        rendered_html = render_markdown(ch.content)
        content_hash = compute_content_hash(ch.content)
        reading_time = compute_reading_time(word_count)
        toc = extract_toc(ch.content)

        chapter_qualities.append((word_count, quality))
        total_word_count += word_count

        chapter_data.append({
            "doc_id": doc_id,
            "slug": chapter_slug,
            "title": ch.title,
            "subtitle": ch.subtitle,
            "content": ch.content,
            "rendered_html": rendered_html,
            "content_hash": content_hash,
            "word_count": word_count,
            "reading_time": reading_time,
            "toc": toc,
            "quality": quality,
            "chapter_number": i,
        })

    # Book-level quality
    book_quality = score_book_quality(chapter_qualities)

    # Create book
    book = Book(
        id=book_id,
        account_id=account_id,
        slug=book_slug,
        title=body.title,
        subtitle=body.subtitle,
        description=body.description,
        format=body.format,
        authors=[a.model_dump() for a in body.authors],
        tags=body.tags,
        doc_metadata=body.metadata,
        cover_image_url=body.cover_image_url,
        listed=body.options.listed,
        quality_score=book_quality.total,
        quality_detail={
            "structure": book_quality.structure,
            "substance": book_quality.substance,
            "tone": book_quality.tone,
            "attribution": book_quality.attribution,
        },
        author_gravity=gravity_level,
        chapter_count=len(body.chapters),
        total_word_count=total_word_count,
    )
    db.add(book)

    # Create documents and chapters
    chapter_responses = []
    for cd in chapter_data:
        doc = Document(
            id=cd["doc_id"],
            account_id=account_id,
            slug=cd["slug"],
            title=cd["title"],
            subtitle=cd["subtitle"],
            format=body.format,
            current_version=1,
            authors=[a.model_dump() for a in body.authors],
            doc_metadata=body.metadata,
            tags=body.tags,
            listed=body.options.listed,
            quality_score=cd["quality"].total,
            quality_detail={
                "structure": cd["quality"].structure,
                "substance": cd["quality"].substance,
                "tone": cd["quality"].tone,
                "attribution": cd["quality"].attribution,
            },
            author_gravity=gravity_level,
            book_id=book_id,
        )
        db.add(doc)

        version = DocumentVersion(
            document_id=cd["doc_id"],
            version=1,
            content=cd["content"],
            content_hash=cd["content_hash"],
            rendered_html=cd["rendered_html"],
            word_count=cd["word_count"],
            reading_time=cd["reading_time"],
            toc=cd["toc"],
        )
        db.add(version)

        bc = BookChapter(
            book_id=book_id,
            document_id=cd["doc_id"],
            chapter_number=cd["chapter_number"],
            chapter_title=cd["title"],
        )
        db.add(bc)

        chapter_responses.append(ChapterResponse(
            chapter_number=cd["chapter_number"],
            document_id=cd["doc_id"],
            title=cd["title"],
            url=f"{settings.base_url}/{cd['slug']}",
            permanent_url=f"{settings.base_url}/d/{cd['doc_id']}",
            word_count=cd["word_count"],
            reading_time_minutes=cd["reading_time"],
            quality_score=cd["quality"].total,
        ))

        all_urls.append(f"{settings.base_url}/{cd['slug']}")

    await db.commit()

    # Notify search engines
    if body.options.listed:
        try:
            all_urls.insert(0, f"{settings.base_url}/{book_slug}")
            await _notify_search_engines(all_urls)
        except Exception:
            pass

    return PublishBookResponse(
        id=book_id,
        url=f"{settings.base_url}/{book_slug}",
        title=body.title,
        chapters=chapter_responses,
        quality_score=book_quality.total,
        quality_breakdown=QualityBreakdown(
            structure=book_quality.structure,
            substance=book_quality.substance,
            tone=book_quality.tone,
            attribution=book_quality.attribution,
        ),
        total_word_count=total_word_count,
        chapter_count=len(body.chapters),
        author_gravity=gravity_level,
    )


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: AsyncSession = Depends(get_db)):
    """Get book metadata and chapter listing."""
    book = await _get_book_or_404(book_id, db)

    # Load chapters with their documents and versions
    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id).order_by(BookChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()

    chapter_responses = []
    for ch in chapters:
        doc_result = await db.execute(select(Document).where(Document.id == ch.document_id))
        doc = doc_result.scalar_one_or_none()
        if not doc or doc.deleted_at:
            continue
        ver_result = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == doc.id,
                DocumentVersion.version == doc.current_version,
            )
        )
        version = ver_result.scalar_one_or_none()
        chapter_responses.append(_chapter_response(ch, doc, version))

    return BookResponse(
        id=book.id,
        title=book.title,
        subtitle=book.subtitle,
        description=book.description,
        format=book.format,
        slug=book.slug,
        authors=[AuthorInfo(**a) for a in (book.authors or [])],
        tags=book.tags or [],
        cover_image_url=book.cover_image_url,
        quality_score=book.quality_score,
        author_gravity=book.author_gravity,
        chapter_count=book.chapter_count,
        total_word_count=book.total_word_count,
        listed=book.listed,
        created_at=book.created_at,
        updated_at=book.updated_at,
        url=f"{settings.base_url}/{book.slug}" if book.slug else None,
        chapters=chapter_responses,
    )


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    body: BookUpdateRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Update book metadata."""
    book = await _get_book_or_404(book_id, db)
    if book.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    if body.title is not None:
        book.title = body.title
    if body.subtitle is not None:
        book.subtitle = body.subtitle
    if body.description is not None:
        book.description = body.description
    if body.format is not None:
        book.format = body.format
    if body.authors is not None:
        book.authors = [a.model_dump() for a in body.authors]
    if body.tags is not None:
        book.tags = body.tags
    if body.metadata is not None:
        book.doc_metadata = body.metadata
    if body.listed is not None:
        book.listed = body.listed
    if body.cover_image_url is not None:
        book.cover_image_url = body.cover_image_url
    if body.slug is not None:
        new_slug = body.slug.strip().lower()
        if new_slug != book.slug:
            existing = await db.execute(select(Book).where(Book.slug == new_slug, Book.deleted_at.is_(None), Book.id != book.id))
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Book slug already taken")
            book.slug = new_slug

    book.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(book)

    # Reuse get_book to build response
    return await get_book(book_id, db)


@router.delete("/books/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a book and all its chapters."""
    book = await _get_book_or_404(book_id, db)
    if book.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    now = datetime.now(UTC)
    book.deleted_at = now

    # Soft-delete all chapter documents
    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id)
    )
    chapters = chapters_result.scalars().all()
    for ch in chapters:
        doc_result = await db.execute(select(Document).where(Document.id == ch.document_id))
        doc = doc_result.scalar_one_or_none()
        if doc and not doc.deleted_at:
            doc.deleted_at = now

    await db.commit()

    try:
        urls = [f"{settings.base_url}/{book.slug}"]
        await _notify_search_engines(urls)
    except Exception:
        pass


@router.post("/books/{book_id}/chapters", response_model=ChapterResponse, status_code=201)
@limiter.limit("60/hour")
async def add_chapter(
    book_id: str,
    body: AddChapterRequest,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Add a chapter to an existing book."""
    book = await _get_book_or_404(book_id, db)
    if book.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    word_count = compute_word_count(body.content)
    if word_count < MIN_CHAPTER_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Chapter must be at least {MIN_CHAPTER_WORD_COUNT} words (got {word_count})",
        )

    if not any(line.strip().startswith("#") for line in body.content.split("\n")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Chapter must contain at least one heading",
        )

    # Determine chapter position
    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id).order_by(BookChapter.chapter_number)
    )
    existing_chapters = chapters_result.scalars().all()
    max_num = max((ch.chapter_number for ch in existing_chapters), default=0)

    if body.position and body.position <= max_num:
        # Shift existing chapters at and after this position
        for ch in existing_chapters:
            if ch.chapter_number >= body.position:
                ch.chapter_number += 1
        chapter_number = body.position
    else:
        chapter_number = max_num + 1

    # Create document
    doc_id = generate_doc_id()
    chapter_slug = body.slug or _generate_chapter_slug(book.slug, chapter_number, body.title)
    chapter_slug = await ensure_unique_slug(chapter_slug, db)

    quality = score_quality(body.title, body.content)
    rendered_html = render_markdown(body.content)
    content_hash = compute_content_hash(body.content)
    reading_time = compute_reading_time(word_count)
    toc = extract_toc(body.content)

    doc = Document(
        id=doc_id,
        account_id=auth.account.id,
        slug=chapter_slug,
        title=body.title,
        subtitle=body.subtitle,
        format=book.format,
        current_version=1,
        authors=book.authors,
        doc_metadata=book.doc_metadata,
        tags=book.tags,
        listed=book.listed,
        quality_score=quality.total,
        quality_detail={
            "structure": quality.structure,
            "substance": quality.substance,
            "tone": quality.tone,
            "attribution": quality.attribution,
        },
        author_gravity=auth.gravity_level,
        book_id=book.id,
    )
    db.add(doc)

    version = DocumentVersion(
        document_id=doc_id,
        version=1,
        content=body.content,
        content_hash=content_hash,
        rendered_html=rendered_html,
        word_count=word_count,
        reading_time=reading_time,
        toc=toc,
    )
    db.add(version)

    bc = BookChapter(
        book_id=book.id,
        document_id=doc_id,
        chapter_number=chapter_number,
        chapter_title=body.title,
    )
    db.add(bc)

    # Update book aggregates
    book.chapter_count = max_num + 1
    book.total_word_count = (book.total_word_count or 0) + word_count
    book.updated_at = datetime.now(UTC)

    await db.commit()

    if book.listed:
        try:
            await _notify_search_engines([
                f"{settings.base_url}/{chapter_slug}",
                f"{settings.base_url}/{book.slug}",
            ])
        except Exception:
            pass

    return ChapterResponse(
        chapter_number=chapter_number,
        document_id=doc_id,
        title=body.title,
        url=f"{settings.base_url}/{chapter_slug}",
        permanent_url=f"{settings.base_url}/d/{doc_id}",
        word_count=word_count,
        reading_time_minutes=reading_time,
        quality_score=quality.total,
    )


@router.put("/books/{book_id}/chapters/reorder", response_model=list[ChapterResponse])
async def reorder_chapters(
    book_id: str,
    body: ReorderChaptersRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Reorder chapters by providing document IDs in desired order."""
    book = await _get_book_or_404(book_id, db)
    if book.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id)
    )
    chapters = {ch.document_id: ch for ch in chapters_result.scalars().all()}

    if set(body.chapter_order) != set(chapters.keys()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="chapter_order must contain exactly all chapter document IDs",
        )

    for i, doc_id in enumerate(body.chapter_order, 1):
        chapters[doc_id].chapter_number = i

    book.updated_at = datetime.now(UTC)
    await db.commit()

    # Build response
    result = []
    for doc_id in body.chapter_order:
        ch = chapters[doc_id]
        doc_result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = doc_result.scalar_one_or_none()
        ver_result = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == doc_id,
                DocumentVersion.version == doc.current_version,
            )
        )
        version = ver_result.scalar_one_or_none()
        result.append(_chapter_response(ch, doc, version))

    return result


@router.delete("/books/{book_id}/chapters/{doc_id}", status_code=204)
async def detach_chapter(
    book_id: str,
    doc_id: str,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Detach a chapter from a book (document survives as standalone)."""
    book = await _get_book_or_404(book_id, db)
    if book.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    ch_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id, BookChapter.document_id == doc_id)
    )
    chapter = ch_result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found in this book")

    removed_num = chapter.chapter_number

    # Remove the chapter link
    await db.delete(chapter)

    # Clear book_id on the document
    doc_result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = doc_result.scalar_one_or_none()
    if doc:
        doc.book_id = None

    # Renumber remaining chapters
    remaining_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id).order_by(BookChapter.chapter_number)
    )
    remaining = remaining_result.scalars().all()
    for ch in remaining:
        if ch.chapter_number > removed_num:
            ch.chapter_number -= 1

    book.chapter_count = len(remaining)
    book.updated_at = datetime.now(UTC)

    await db.commit()
