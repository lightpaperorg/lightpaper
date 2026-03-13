"""Reading routes: GET /{slug} and GET /d/{doc_id} with content negotiation."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Account, Book, BookChapter, Credential, Document, DocumentVersion, Narration, NarrationChapter
from app.rate_limit import limiter
from app.schemas import AuthorInfo, DocumentResponse
from app.services.gravity import get_gravity_badges

router = APIRouter(tags=["reading"])

# Reserved paths that should NOT match the /{slug} catch-all
RESERVED_PREFIXES = {"v1", "health", "robots.txt", "sitemap.xml", "llms.txt", "og", "d", "static", "@", "write"}

# Normalize legacy format values to new taxonomy
FORMAT_NORMALIZE = {
    "markdown": "post",
    "academic": "paper",
    "report": "paper",
    "tutorial": "post",
}


async def _load_doc_by_slug(slug: str, db: AsyncSession):
    result = await db.execute(select(Document).where(Document.slug == slug, Document.deleted_at.is_(None)))
    return result.scalar_one_or_none()


async def _load_doc_by_id(doc_id: str, db: AsyncSession):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc and doc.deleted_at is not None:
        raise HTTPException(status_code=410, detail="Document has been deleted")
    return doc


async def _load_version(doc_id: str, version: int, db: AsyncSession):
    result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == doc_id,
            DocumentVersion.version == version,
        )
    )
    return result.scalar_one_or_none()


def _wants_json(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "application/json" in accept and "text/html" not in accept


async def _render_html(doc: Document, version: DocumentVersion, db: AsyncSession) -> HTMLResponse:
    import os

    from jinja2 import Environment, FileSystemLoader

    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("document.html")

    # Gravity badges — load account + credentials for accurate display
    gravity_badges = []
    linkedin_url = None
    orcid_id = None
    if doc.account_id:
        acct_result = await db.execute(select(Account).where(Account.id == doc.account_id))
        account = acct_result.scalar_one_or_none()
        if account:
            cred_result = await db.execute(select(Credential).where(Credential.account_id == account.id))
            creds = cred_result.scalars().all()
            gravity_badges = get_gravity_badges(
                account.verified_domain,
                account.verified_linkedin,
                account.orcid_id,
                credentials=creds,
            )
            linkedin_url = account.linkedin_url
            orcid_id = account.orcid_id

    # Format date
    created_at_formatted = doc.created_at.strftime("%b %d, %Y") if doc.created_at else ""

    # Canonical URL = slug URL (matches sitemap); permanent URL kept for footer
    slug_url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"

    # Book/chapter context
    book_title = None
    book_slug = None
    chapter_number = None
    total_chapters = None
    prev_chapter = None
    next_chapter = None

    # Check for narration audio
    audio_url = None
    if doc.book_id:
        narration_result = await db.execute(
            select(Narration).where(
                Narration.book_id == doc.book_id,
                Narration.audio_ready.is_(True),
            )
        )
        narration = narration_result.scalar_one_or_none()
        if narration:
            ch_audio_result = await db.execute(
                select(NarrationChapter).where(
                    NarrationChapter.narration_id == narration.id,
                    NarrationChapter.document_id == doc.id,
                    NarrationChapter.audio_url.isnot(None),
                )
            )
            ch_audio = ch_audio_result.scalar_one_or_none()
            if ch_audio:
                audio_url = ch_audio.audio_url

    if doc.book_id:
        book_result = await db.execute(select(Book).where(Book.id == doc.book_id, Book.deleted_at.is_(None)))
        book = book_result.scalar_one_or_none()
        if book:
            book_title = book.title
            book_slug = book.slug

            chapters_result = await db.execute(
                select(BookChapter).where(BookChapter.book_id == book.id).order_by(BookChapter.chapter_number)
            )
            all_chapters = chapters_result.scalars().all()
            total_chapters = len(all_chapters)

            for idx, ch in enumerate(all_chapters):
                if ch.document_id == doc.id:
                    chapter_number = ch.chapter_number
                    if idx > 0:
                        prev_ch = all_chapters[idx - 1]
                        prev_doc_result = await db.execute(select(Document).where(Document.id == prev_ch.document_id))
                        prev_doc = prev_doc_result.scalar_one_or_none()
                        if prev_doc and not prev_doc.deleted_at:
                            prev_chapter = {
                                "title": prev_doc.title or prev_ch.chapter_title,
                                "url": f"/{prev_doc.slug}" if prev_doc.slug else f"/d/{prev_doc.id}",
                            }
                    if idx < len(all_chapters) - 1:
                        next_ch = all_chapters[idx + 1]
                        next_doc_result = await db.execute(select(Document).where(Document.id == next_ch.document_id))
                        next_doc = next_doc_result.scalar_one_or_none()
                        if next_doc and not next_doc.deleted_at:
                            next_chapter = {
                                "title": next_doc.title or next_ch.chapter_title,
                                "url": f"/{next_doc.slug}" if next_doc.slug else f"/d/{next_doc.id}",
                            }
                    break

    html = template.render(
        title=doc.title,
        subtitle=doc.subtitle,
        authors=doc.authors or [],
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        created_at_formatted=created_at_formatted,
        rendered_html=version.rendered_html or "",
        word_count=version.word_count,
        reading_time=version.reading_time,
        quality_score=doc.quality_score,
        content_hash=version.content_hash,
        canonical_url=slug_url,
        permanent_url=f"{settings.base_url}/d/{doc.id}",
        og_image_url=f"{settings.base_url}/og/{doc.id}.png",
        gravity_badges=gravity_badges,
        linkedin_url=linkedin_url,
        orcid_id=orcid_id,
        format=FORMAT_NORMALIZE.get(doc.format, doc.format) or "post",
        book_title=book_title,
        book_slug=book_slug,
        chapter_number=chapter_number,
        total_chapters=total_chapters,
        prev_chapter=prev_chapter,
        next_chapter=next_chapter,
        audio_url=audio_url,
    )
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "public, max-age=3600"},
    )


def _render_json(doc: Document, version: DocumentVersion) -> JSONResponse:
    resp = DocumentResponse(
        id=doc.id,
        title=doc.title,
        subtitle=doc.subtitle,
        content=version.content,
        format=doc.format,
        slug=doc.slug,
        authors=[AuthorInfo(**a) for a in (doc.authors or [])],
        metadata=doc.doc_metadata or {},
        tags=doc.tags or [],
        word_count=version.word_count,
        reading_time_minutes=version.reading_time,
        quality_score=doc.quality_score,
        author_gravity=doc.author_gravity,
        current_version=doc.current_version,
        listed=doc.listed,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        permanent_url=f"{settings.base_url}/d/{doc.id}",
        url=f"{settings.base_url}/{doc.slug}" if doc.slug else None,
    )
    return JSONResponse(content=resp.model_dump(mode="json"))


@router.get("/d/{doc_id}")
@limiter.limit("120/minute")
async def read_by_id(doc_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    doc = await _load_doc_by_id(doc_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    version = await _load_version(doc.id, doc.current_version, db)
    if not version:
        raise HTTPException(status_code=500, detail="Version not found")

    if _wants_json(request):
        return _render_json(doc, version)
    return await _render_html(doc, version, db)


@router.get("/books/{slug}")
@limiter.limit("120/minute")
async def read_book_redirect(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Redirect /books/{slug} to /{slug} for backward compatibility."""
    from fastapi.responses import RedirectResponse
    result = await db.execute(select(Book).where(Book.slug == slug, Book.deleted_at.is_(None)))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return RedirectResponse(url=f"/{book.slug}", status_code=301)



@router.get("/{slug:path}")
@limiter.limit("120/minute")
async def read_by_slug(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    # Skip reserved paths
    first_segment = slug.split("/")[0] if "/" in slug else slug
    if first_segment in RESERVED_PREFIXES or first_segment.startswith("@"):
        raise HTTPException(status_code=404, detail="Not found")

    # Try document first
    doc = await _load_doc_by_slug(slug, db)
    if doc:
        version = await _load_version(doc.id, doc.current_version, db)
        if not version:
            raise HTTPException(status_code=500, detail="Version not found")
        if _wants_json(request):
            return _render_json(doc, version)
        return await _render_html(doc, version, db)

    # Try book
    book_result = await db.execute(select(Book).where(Book.slug == slug, Book.deleted_at.is_(None)))
    book = book_result.scalar_one_or_none()
    if book:
        return await _render_book(book, request, db)

    raise HTTPException(status_code=404, detail="Not found")


async def _render_book(book: "Book", request: Request, db: AsyncSession):
    """Render a book landing page (HTML or JSON)."""
    chapters_result = await db.execute(
        select(BookChapter).where(BookChapter.book_id == book.id).order_by(BookChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()

    chapter_list = []
    total_reading_time = 0
    for ch in chapters:
        doc_result = await db.execute(select(Document).where(Document.id == ch.document_id, Document.deleted_at.is_(None)))
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
        rt = ver.reading_time if ver else 0
        total_reading_time += rt or 0
        chapter_list.append({
            "chapter_number": ch.chapter_number,
            "title": doc.title or ch.chapter_title,
            "url": f"/{doc.slug}" if doc.slug else f"/d/{doc.id}",
            "reading_time_minutes": rt,
            "word_count": ver.word_count if ver else 0,
            "quality_score": doc.quality_score,
            "document_id": doc.id,
        })

    if _wants_json(request):
        from app.schemas import AuthorInfo, BookResponse, ChapterResponse

        ch_responses = [
            ChapterResponse(
                chapter_number=c["chapter_number"],
                document_id=c["document_id"],
                title=c["title"],
                url=f"{settings.base_url}{c['url']}",
                permanent_url=f"{settings.base_url}/d/{c['document_id']}",
                word_count=c["word_count"] or 0,
                reading_time_minutes=c["reading_time_minutes"] or 0,
                quality_score=c["quality_score"] or 0,
            )
            for c in chapter_list
        ]
        resp = BookResponse(
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
            url=f"{settings.base_url}/{book.slug}",
            chapters=ch_responses,
        )
        return JSONResponse(content=resp.model_dump(mode="json"))

    import os

    from jinja2 import Environment, FileSystemLoader

    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("book.html")

    gravity_badges = []
    linkedin_url = None
    orcid_id = None
    if book.account_id:
        acct_result = await db.execute(select(Account).where(Account.id == book.account_id))
        account = acct_result.scalar_one_or_none()
        if account:
            cred_result = await db.execute(select(Credential).where(Credential.account_id == account.id))
            creds = cred_result.scalars().all()
            gravity_badges = get_gravity_badges(
                account.verified_domain,
                account.verified_linkedin,
                account.orcid_id,
                credentials=creds,
            )
            linkedin_url = account.linkedin_url
            orcid_id = account.orcid_id

    rendered_description = None
    if book.description:
        from app.services.renderer import render_markdown
        rendered_description = render_markdown(book.description)

    created_at_formatted = book.created_at.strftime("%b %d, %Y") if book.created_at else ""

    html = template.render(
        title=book.title,
        subtitle=book.subtitle,
        description=book.description,
        authors=book.authors or [],
        created_at=book.created_at.isoformat() if book.created_at else "",
        updated_at=book.updated_at.isoformat() if book.updated_at else "",
        created_at_formatted=created_at_formatted,
        chapter_count=book.chapter_count,
        total_word_count=book.total_word_count,
        total_reading_time=total_reading_time,
        quality_score=book.quality_score,
        chapters=chapter_list,
        canonical_url=f"{settings.base_url}/{book.slug}",
        permanent_url=f"{settings.base_url}/{book.slug}",
        og_image_url=f"{settings.base_url}/og/{book.id}.png",
        gravity_badges=gravity_badges,
        linkedin_url=linkedin_url,
        orcid_id=orcid_id,
        format=book.format or "post",
        rendered_description=rendered_description,
    )
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "public, max-age=3600"},
    )
