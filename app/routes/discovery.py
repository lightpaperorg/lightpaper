"""Discovery routes: robots.txt, sitemap.xml, llms.txt, OG images."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Document, DocumentVersion
from app.services.og_image import generate_og_image
from app.services.gravity import get_gravity_badges

router = APIRouter(tags=["discovery"])


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return f"""User-agent: *
Allow: /
Disallow: /v1/account
Disallow: /v1/account/

Sitemap: {settings.base_url}/sitemap.xml
"""


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    return f"""# lightpaper.org

> API-first publishing platform. One HTTP call, one permanent URL.

lightpaper.org is a publishing platform designed for AI agents and humans.
Publish documents via a single API call and get beautiful, permanent, discoverable URLs.

## API

Base URL: {settings.base_url}

- POST /v1/publish — Publish a document (returns permanent URL + quality score)
- GET /v1/search?q=query — Search documents
- GET /v1/documents/{{id}} — Get document metadata + content (JSON)
- GET /{{slug}} — Read document (HTML or JSON via Accept header)
- GET /d/{{id}} — Read by permanent ID

## Authentication

- Anonymous: No auth needed (5 publishes/hour, unlisted)
- API key: Bearer lp_live_xxx or lp_free_xxx
- Firebase: Bearer <id_token>

## Content Negotiation

Same URL serves HTML (browsers) or JSON (agents) via Accept header:
- Accept: text/html → rendered HTML page
- Accept: application/json → structured JSON

## MCP Server

lightpaper.org provides an MCP server with tools:
- publish_lightpaper, search_lightpapers, get_lightpaper, update_lightpaper, list_my_lightpapers

## OpenAPI

Full API specification: {settings.base_url}/v1/openapi.json
"""


@router.get("/sitemap.xml")
async def sitemap_xml(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document).where(
            Document.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.quality_score >= 40,
        ).order_by(Document.updated_at.desc())
    )
    docs = result.scalars().all()

    urls = []
    for doc in docs:
        slug_url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"
        lastmod = doc.updated_at.strftime("%Y-%m-%d") if doc.updated_at else ""
        urls.append(f"""  <url>
    <loc>{slug_url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{settings.base_url}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
{"".join(urls)}
</urlset>"""

    return Response(content=xml, media_type="application/xml")


@router.get("/og/{doc_id}.png")
async def og_image(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get reading time from current version
    ver_result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == doc.id,
            DocumentVersion.version == doc.current_version,
        )
    )
    version = ver_result.scalar_one_or_none()

    # Author name
    author_name = None
    if doc.authors:
        names = [a.get("name", a.get("handle", "")) for a in doc.authors]
        author_name = " & ".join(names[:3])

    # Badges from gravity level
    badges = []
    if doc.author_gravity >= 1:
        badges.append("Domain \u2713")
    if doc.author_gravity >= 2:
        badges.append("LinkedIn \u2713")
    if doc.author_gravity >= 3:
        badges.append("ORCID \u2713")

    img_bytes = generate_og_image(
        title=doc.title,
        subtitle=doc.subtitle,
        quality_score=doc.quality_score,
        author_name=author_name,
        gravity_badges=badges,
        reading_time=version.reading_time if version else None,
    )

    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )
