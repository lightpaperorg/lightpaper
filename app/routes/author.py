"""Author profile routes: GET /@{handle} with content negotiation."""

import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Account, Credential, Document, DocumentVersion
from app.rate_limit import limiter
from app.services.gravity import get_gravity_badges, compute_gravity_level

router = APIRouter(tags=["author"])

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def _wants_json(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "application/json" in accept and "text/html" not in accept


@router.get("/@{handle}")
@limiter.limit("120/minute")
async def author_profile(handle: str, request: Request, db: AsyncSession = Depends(get_db)):
    # Look up account by handle
    result = await db.execute(
        select(Account).where(Account.handle == handle, Account.deleted_at.is_(None))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Author not found")

    # Load credentials for badges
    cred_result = await db.execute(
        select(Credential).where(Credential.account_id == account.id)
    )
    creds = cred_result.scalars().all()

    gravity_badges = get_gravity_badges(
        account.verified_domain,
        account.verified_linkedin,
        account.orcid_id,
        credentials=creds,
    )
    gravity_level = compute_gravity_level(
        account.verified_domain,
        account.verified_linkedin,
        account.orcid_id,
        credentials=creds,
    )

    # Load listed, non-deleted documents with reading_time from current version
    doc_result = await db.execute(
        select(Document, DocumentVersion.reading_time).join(
            DocumentVersion,
            (DocumentVersion.document_id == Document.id)
            & (DocumentVersion.version == Document.current_version),
        ).where(
            Document.account_id == account.id,
            Document.listed.is_(True),
            Document.deleted_at.is_(None),
        ).order_by(Document.created_at.desc())
    )
    doc_rows = doc_result.all()

    documents = []
    for doc, reading_time in doc_rows:
        documents.append({
            "id": doc.id,
            "title": doc.title,
            "subtitle": doc.subtitle,
            "slug": doc.slug,
            "url": f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}",
            "quality_score": doc.quality_score,
            "reading_time": reading_time,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "created_at_formatted": doc.created_at.strftime("%b %d, %Y") if doc.created_at else "",
        })

    if _wants_json(request):
        return JSONResponse(
            content={
                "handle": account.handle,
                "display_name": account.display_name,
                "bio": account.bio,
                "gravity_level": gravity_level,
                "gravity_badges": gravity_badges,
                "member_since": account.created_at.isoformat() if account.created_at else None,
                "documents": documents,
            },
            headers={"Cache-Control": "public, max-age=600"},
        )

    # HTML rendering
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template("author.html")

    html = template.render(
        handle=account.handle,
        display_name=account.display_name or account.handle,
        bio=account.bio,
        gravity_level=gravity_level,
        gravity_badges=gravity_badges,
        member_since=account.created_at.strftime("%b %Y") if account.created_at else "",
        documents=documents,
        document_count=len(documents),
        base_url=settings.base_url,
        profile_url=f"{settings.base_url}/@{account.handle}",
    )
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "public, max-age=600"},
    )
