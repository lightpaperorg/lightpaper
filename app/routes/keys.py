"""API key management: CRUD /v1/account/keys."""

import secrets

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.database import get_db
from app.models import ApiKey
from app.schemas import KeyCreateRequest, KeyCreateResponse, KeyResponse

router = APIRouter(prefix="/v1/account", tags=["keys"])

KEY_LIMITS = {"free": 1, "pro": 3, "team": 10}


def _generate_key(tier: str) -> str:
    """Generate an API key: lp_{tier}_ + 24-char token."""
    prefix_map = {"free": "lp_free_", "pro": "lp_live_", "test": "lp_test_"}
    prefix = prefix_map.get(tier, "lp_free_")
    token = secrets.token_urlsafe(24)
    return f"{prefix}{token}"


@router.post("/keys", response_model=KeyCreateResponse, status_code=201)
async def create_key(
    body: KeyCreateRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    # Check key limit
    limit = KEY_LIMITS.get(auth.account.tier, 1)
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.account_id == auth.account.id,
            ApiKey.revoked_at.is_(None),
        )
    )
    active_keys = result.scalars().all()
    if len(active_keys) >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{auth.account.tier} tier limited to {limit} key(s). Revoke an existing key first.",
        )

    # Generate key
    full_key = _generate_key(body.tier)
    key_hash = bcrypt.hashpw(full_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    key_prefix = full_key[:8]

    api_key = ApiKey(
        account_id=auth.account.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        tier=body.tier,
        label=body.label,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return KeyCreateResponse(
        key=full_key,
        prefix=key_prefix,
        label=api_key.label,
        tier=api_key.tier,
        created_at=api_key.created_at,
    )


@router.get("/keys", response_model=list[KeyResponse])
async def list_keys(
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.account_id == auth.account.id,
            ApiKey.revoked_at.is_(None),
        ).order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()

    return [
        KeyResponse(
            prefix=k.key_prefix,
            label=k.label,
            tier=k.tier,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.delete("/keys/{prefix}", status_code=204)
async def revoke_key(
    prefix: str,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.account_id == auth.account.id,
            ApiKey.key_prefix == prefix,
            ApiKey.revoked_at.is_(None),
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")

    from datetime import datetime, timezone
    key.revoked_at = datetime.now(timezone.utc)
    await db.commit()
