"""GET /v1/search — full-text search with quality × gravity ranking."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import case, cast, func, literal_column, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Document
from app.schemas import AuthorInfo, SearchResponse, SearchResult
from app.rate_limit import limiter
from app.services.gravity import GRAVITY_MULTIPLIERS
from app.utils import get_client_ip

router = APIRouter(prefix="/v1", tags=["search"])


@router.get("/search", response_model=SearchResponse)
@limiter.limit("60/minute")
async def search_documents(
    request: Request,
    q: str | None = Query(None, description="Full-text search query"),
    tags: str | None = Query(None, description="Comma-separated tag filter"),
    author: str | None = Query(None, description="Filter by author handle"),
    min_quality: int = Query(40, ge=0, le=100, description="Minimum quality score"),
    sort: str = Query("relevance", description="Sort: relevance, recent, quality"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    # Base query — only listed, non-deleted docs
    base = select(Document).where(
        Document.deleted_at.is_(None),
        Document.listed.is_(True),
        Document.quality_score >= min_quality,
    )

    # Full-text search
    if q:
        ts_query = func.plainto_tsquery("english", q)
        base = base.where(Document.search_vector.op("@@")(ts_query))

    # Tag filter (parameterized — no SQL injection)
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        for tag in tag_list:
            base = base.where(Document.tags.op("@>")(cast([tag], JSONB)))

    # Author filter (parameterized — no SQL injection)
    if author:
        base = base.where(
            Document.authors.op("@>")(cast([{"handle": author}], JSONB))
        )

    # Count total
    count_query = select(func.count()).select_from(base.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Sorting
    if sort == "recent":
        base = base.order_by(Document.created_at.desc())
    elif sort == "quality":
        base = base.order_by(Document.quality_score.desc())
    else:
        # Relevance: quality_score × gravity_multiplier
        gravity_case = case(
            (Document.author_gravity == 0, GRAVITY_MULTIPLIERS[0]),
            (Document.author_gravity == 1, GRAVITY_MULTIPLIERS[1]),
            (Document.author_gravity == 2, GRAVITY_MULTIPLIERS[2]),
            (Document.author_gravity == 3, GRAVITY_MULTIPLIERS[3]),
            else_=1.0,
        )
        if q:
            ts_query = func.plainto_tsquery("english", q)
            rank = func.ts_rank(Document.search_vector, ts_query)
            score = rank * Document.quality_score * gravity_case
        else:
            score = Document.quality_score * gravity_case
        base = base.order_by(score.desc())

    # Pagination
    base = base.offset(offset).limit(limit)

    result = await db.execute(base)
    docs = result.scalars().all()

    results = [
        SearchResult(
            id=doc.id,
            title=doc.title,
            subtitle=doc.subtitle,
            url=f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}",
            authors=[AuthorInfo(**a) for a in (doc.authors or [])],
            tags=doc.tags or [],
            quality_score=doc.quality_score,
            word_count=None,  # Would need a join to versions
            created_at=doc.created_at,
        )
        for doc in docs
    ]

    return SearchResponse(results=results, total=total, limit=limit, offset=offset)
