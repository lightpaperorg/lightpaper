"""POST /v1/publish — the entire product in one endpoint."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, authenticate
from app.config import settings
from app.database import get_db
from app.id_gen import generate_doc_id
from app.models import AnonymousPublish, Credential, Document, DocumentVersion
from app.rate_limit import limiter
from app.schemas import PublishRequest, PublishResponse, QualityBreakdown
from app.services.gravity import get_gravity_badges, get_next_level_instructions
from app.services.quality import score_quality
from app.services.renderer import (
    compute_content_hash,
    compute_reading_time,
    compute_word_count,
    extract_toc,
    render_markdown,
)
from app.services.slug import ensure_unique_slug, generate_slug, is_reserved_slug
from app.utils import get_client_ip

router = APIRouter(prefix="/v1", tags=["publish"])

ANONYMOUS_RATE_LIMIT = 5  # per hour per IP
MIN_WORD_COUNT = 300


@router.post("/publish", response_model=PublishResponse, status_code=201)
@limiter.limit("60/hour")
async def publish_document(
    body: PublishRequest,
    request: Request,
    auth: AuthResult = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    # Word count check
    word_count = compute_word_count(body.content)
    if word_count < MIN_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Content must be at least {MIN_WORD_COUNT} words (got {word_count})",
        )

    # Must have at least one heading
    if not any(line.strip().startswith("#") for line in body.content.split("\n")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Content must contain at least one heading (e.g. # Introduction)",
        )

    # Anonymous rate limiting
    is_anonymous = auth.is_anonymous
    if is_anonymous:
        ip = get_client_ip(request)
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        result = await db.execute(
            select(func.count(AnonymousPublish.id)).where(
                AnonymousPublish.ip_address == ip,
                AnonymousPublish.created_at > one_hour_ago,
            )
        )
        count = result.scalar()
        if count >= ANONYMOUS_RATE_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Anonymous publishing limited to {ANONYMOUS_RATE_LIMIT}/hour. Create an account for more.",
            )

    # Generate IDs
    doc_id = generate_doc_id()
    custom_slug = body.options.slug
    if custom_slug and is_reserved_slug(custom_slug):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"The slug '{custom_slug}' is reserved and cannot be used.",
        )
    slug = custom_slug or generate_slug(body.title)
    slug = await ensure_unique_slug(slug, db)

    # Quality scoring
    quality = score_quality(body.title, body.content)

    # Render
    rendered_html = render_markdown(body.content)
    content_hash = compute_content_hash(body.content)
    reading_time = compute_reading_time(word_count)
    toc = extract_toc(body.content)

    # Determine listing and gravity
    listed = body.options.listed and not is_anonymous
    account_id = auth.account.id if auth.account else None
    gravity_level = auth.gravity_level

    # Extract tags from metadata
    tags = body.metadata.get("tags", [])

    # Create document
    doc = Document(
        id=doc_id,
        account_id=account_id,
        slug=slug,
        title=body.title,
        subtitle=body.subtitle,
        format=body.format,
        current_version=1,
        authors=[a.model_dump() for a in body.authors],
        doc_metadata=body.metadata,
        tags=tags,
        listed=listed,
        quality_score=quality.total,
        quality_detail={
            "structure": quality.structure,
            "substance": quality.substance,
            "tone": quality.tone,
            "attribution": quality.attribution,
        },
        author_gravity=gravity_level,
    )
    db.add(doc)

    # Create version
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

    # Flush doc + version so FK references exist before inserting anonymous_publishes
    await db.flush()

    # Track anonymous publish
    if is_anonymous:
        db.add(AnonymousPublish(ip_address=get_client_ip(request), document_id=doc_id))

    await db.commit()
    await db.refresh(doc)

    # Build response
    gravity_badges = []
    gravity_note = None
    if auth.account:
        cred_result = await db.execute(select(Credential).where(Credential.account_id == auth.account.id))
        creds = cred_result.scalars().all()
        gravity_badges = get_gravity_badges(
            auth.account.verified_domain,
            auth.account.verified_linkedin,
            auth.account.orcid_id,
            credentials=creds,
        )
        gravity_note = get_next_level_instructions(gravity_level)
    elif is_anonymous:
        gravity_note = "Create an account to get permanent URLs and author verification"

    return PublishResponse(
        id=doc_id,
        url=f"{settings.base_url}/{slug}",
        permanent_url=f"{settings.base_url}/d/{doc_id}",
        version=1,
        created_at=doc.created_at,
        word_count=word_count,
        reading_time_minutes=reading_time,
        content_hash=content_hash,
        quality_score=quality.total,
        quality_breakdown=QualityBreakdown(
            structure=quality.structure,
            substance=quality.substance,
            tone=quality.tone,
            attribution=quality.attribution,
        ),
        quality_suggestions=quality.suggestions,
        author_gravity=gravity_level,
        author_gravity_badges=gravity_badges,
        gravity_note=gravity_note,
    )
