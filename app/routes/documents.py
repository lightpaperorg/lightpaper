"""GET/PUT/DELETE /v1/documents/{id} — document CRUD."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, authenticate, require_account
from app.config import settings
from app.database import get_db
from app.models import Document, DocumentVersion
from app.schemas import DocumentResponse, DocumentUpdateRequest, AuthorInfo, VersionResponse
from app.services.quality import score_quality
from app.services.renderer import (
    compute_content_hash,
    compute_reading_time,
    compute_word_count,
    extract_toc,
    render_markdown,
)
from app.services.slug import ensure_unique_slug, generate_slug

router = APIRouter(prefix="/v1", tags=["documents"])


async def _get_doc_or_404(doc_id: str, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.deleted_at is not None:
        raise HTTPException(status_code=410, detail="Document has been deleted")
    return doc


async def _get_current_version(doc_id: str, version: int, db: AsyncSession) -> DocumentVersion:
    result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == doc_id,
            DocumentVersion.version == version,
        )
    )
    return result.scalar_one_or_none()


def _doc_to_response(doc: Document, version: DocumentVersion | None) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        subtitle=doc.subtitle,
        content=version.content if version else "",
        format=doc.format,
        slug=doc.slug,
        authors=[AuthorInfo(**a) for a in (doc.authors or [])],
        metadata=doc.doc_metadata or {},
        tags=doc.tags or [],
        word_count=version.word_count if version else None,
        reading_time_minutes=version.reading_time if version else None,
        quality_score=doc.quality_score,
        author_gravity=doc.author_gravity,
        current_version=doc.current_version,
        listed=doc.listed,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        permanent_url=f"{settings.base_url}/d/{doc.id}",
        url=f"{settings.base_url}/{doc.slug}" if doc.slug else None,
    )


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    doc = await _get_doc_or_404(doc_id, db)
    version = await _get_current_version(doc.id, doc.current_version, db)
    return _doc_to_response(doc, version)


@router.put("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: str,
    body: DocumentUpdateRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    doc = await _get_doc_or_404(doc_id, db)

    # Ownership check
    if doc.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this document")

    # Update metadata fields
    if body.title is not None:
        doc.title = body.title
    if body.subtitle is not None:
        doc.subtitle = body.subtitle
    if body.authors is not None:
        doc.authors = [a.model_dump() for a in body.authors]
    if body.metadata is not None:
        doc.doc_metadata = body.metadata
    if body.tags is not None:
        doc.tags = body.tags
    if body.listed is not None:
        doc.listed = body.listed

    # If content changed, create new version
    if body.content is not None:
        new_version_num = doc.current_version + 1
        rendered_html = render_markdown(body.content)
        content_hash = compute_content_hash(body.content)
        word_count = compute_word_count(body.content)
        reading_time = compute_reading_time(word_count)
        toc = extract_toc(body.content)

        version = DocumentVersion(
            document_id=doc.id,
            version=new_version_num,
            content=body.content,
            content_hash=content_hash,
            rendered_html=rendered_html,
            word_count=word_count,
            reading_time=reading_time,
            toc=toc,
        )
        db.add(version)
        doc.current_version = new_version_num

        # Re-score quality
        quality = score_quality(doc.title, body.content)
        doc.quality_score = quality.total
        doc.quality_detail = {
            "structure": quality.structure,
            "substance": quality.substance,
            "tone": quality.tone,
            "attribution": quality.attribution,
        }

    doc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(doc)

    current_version = await _get_current_version(doc.id, doc.current_version, db)
    return _doc_to_response(doc, current_version)


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(
    doc_id: str,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    doc = await _get_doc_or_404(doc_id, db)
    if doc.account_id != auth.account.id:
        raise HTTPException(status_code=403, detail="You do not own this document")

    doc.deleted_at = datetime.now(timezone.utc)
    await db.commit()


@router.get("/documents/{doc_id}/versions", response_model=list[VersionResponse])
async def list_versions(doc_id: str, db: AsyncSession = Depends(get_db)):
    doc = await _get_doc_or_404(doc_id, db)
    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc.id)
        .order_by(DocumentVersion.version.desc())
    )
    versions = result.scalars().all()
    return [
        VersionResponse(
            version=v.version,
            content_hash=v.content_hash,
            word_count=v.word_count,
            reading_time=v.reading_time,
            created_at=v.created_at,
        )
        for v in versions
    ]
