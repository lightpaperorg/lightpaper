"""Account CRUD: POST/GET/DELETE /v1/account."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account, authenticate
from app.config import settings
from app.database import get_db
from app.models import Account, Document
from app.rate_limit import limiter
from app.schemas import AccountCreateRequest, AccountResponse, AuthorInfo, DocumentResponse
from app.services.gravity import get_gravity_badges

router = APIRouter(prefix="/v1", tags=["accounts"])


def _account_response(account: Account) -> AccountResponse:
    badges = get_gravity_badges(
        account.verified_domain,
        account.verified_linkedin,
        account.orcid_id,
    )
    return AccountResponse(
        id=str(account.id),
        handle=account.handle,
        display_name=account.display_name,
        email=account.email,
        bio=account.bio,
        tier=account.tier,
        gravity_level=account.gravity_level,
        gravity_badges=badges,
        verified_domain=account.verified_domain,
        verified_linkedin=account.verified_linkedin,
        orcid_id=account.orcid_id,
        created_at=account.created_at,
    )


@router.post("/account", response_model=AccountResponse, status_code=201)
@limiter.limit("10/hour")
async def create_account(
    request: Request,
    body: AccountCreateRequest,
    auth: AuthResult = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    if auth.firebase_uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase authentication required to create an account",
        )

    # Check if account already exists
    existing = await db.execute(
        select(Account).where(Account.firebase_uid == auth.firebase_uid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Account already exists")

    # Check handle uniqueness
    if body.handle:
        handle_check = await db.execute(
            select(Account).where(Account.handle == body.handle)
        )
        if handle_check.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Handle already taken")

    account = Account(
        firebase_uid=auth.firebase_uid,
        handle=body.handle,
        display_name=body.display_name,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)

    return _account_response(account)


@router.get("/account", response_model=AccountResponse)
async def get_account(auth: AuthResult = Depends(require_account)):
    return _account_response(auth.account)


@router.delete("/account", status_code=204)
async def delete_account(
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """GDPR hard-delete: cascades to all documents, versions, keys."""
    await db.delete(auth.account)
    await db.commit()


@router.get("/account/documents")
async def list_account_documents(
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.account_id == auth.account.id,
            Document.deleted_at.is_(None),
        ).order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    return [
        {
            "id": doc.id,
            "title": doc.title,
            "slug": doc.slug,
            "quality_score": doc.quality_score,
            "listed": doc.listed,
            "url": f"{settings.base_url}/{doc.slug}" if doc.slug else None,
            "permanent_url": f"{settings.base_url}/d/{doc.id}",
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
        }
        for doc in docs
    ]
