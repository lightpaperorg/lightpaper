"""Reading routes: GET /{slug} and GET /d/{doc_id} with content negotiation."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Document, DocumentVersion
from app.schemas import AuthorInfo, DocumentResponse
from app.services.gravity import get_gravity_badges

router = APIRouter(tags=["reading"])

# Reserved paths that should NOT match the /{slug} catch-all
RESERVED_PREFIXES = {"v1", "health", "robots.txt", "sitemap.xml", "llms.txt", "og", "d", "static"}


async def _load_doc_by_slug(slug: str, db: AsyncSession):
    result = await db.execute(
        select(Document).where(Document.slug == slug, Document.deleted_at.is_(None))
    )
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


def _render_html(doc: Document, version: DocumentVersion) -> HTMLResponse:
    from jinja2 import Environment, FileSystemLoader
    import os

    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("document.html")

    # Gravity badges
    gravity_badges = []
    if doc.account_id:
        # Simple badges from author_gravity level
        if doc.author_gravity >= 1:
            gravity_badges.append("Domain \u2713")
        if doc.author_gravity >= 2:
            gravity_badges.append("LinkedIn \u2713")
        if doc.author_gravity >= 3:
            gravity_badges.append("ORCID \u2713")

    # Format date
    created_at_formatted = doc.created_at.strftime("%b %d, %Y") if doc.created_at else ""

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
        permanent_url=f"{settings.base_url}/d/{doc.id}",
        og_image_url=f"{settings.base_url}/og/{doc.id}.png",
        gravity_badges=gravity_badges,
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
async def read_by_id(doc_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    doc = await _load_doc_by_id(doc_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    version = await _load_version(doc.id, doc.current_version, db)
    if not version:
        raise HTTPException(status_code=500, detail="Version not found")

    if _wants_json(request):
        return _render_json(doc, version)
    return _render_html(doc, version)


@router.get("/{slug:path}")
async def read_by_slug(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    # Skip reserved paths
    first_segment = slug.split("/")[0] if "/" in slug else slug
    if first_segment in RESERVED_PREFIXES:
        raise HTTPException(status_code=404, detail="Not found")

    doc = await _load_doc_by_slug(slug, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    version = await _load_version(doc.id, doc.current_version, db)
    if not version:
        raise HTTPException(status_code=500, detail="Version not found")

    if _wants_json(request):
        return _render_json(doc, version)
    return _render_html(doc, version)
