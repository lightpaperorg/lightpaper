"""Agent-driven onboarding: POST /v1/onboard — one-call account + API key creation."""

import secrets

import bcrypt
import firebase_admin
from firebase_admin import auth as firebase_auth
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Account, ApiKey
from app.rate_limit import limiter
from app.schemas import OnboardRequest, OnboardResponse
from app.services.gravity import get_next_level_instructions

router = APIRouter(prefix="/v1", tags=["onboard"])


def _generate_key(tier: str) -> str:
    """Generate an API key: lp_{tier}_ + 24-char token."""
    prefix_map = {"free": "lp_free_", "pro": "lp_live_", "test": "lp_test_"}
    prefix = prefix_map.get(tier, "lp_free_")
    token = secrets.token_urlsafe(24)
    return f"{prefix}{token}"


@router.post("/onboard", response_model=OnboardResponse, status_code=201)
@limiter.limit("5/hour")
async def onboard(
    request: Request,
    body: OnboardRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a Firebase user + lightpaper account + API key in one call.

    Designed for agent-driven flows where no browser is available.
    """
    # Create Firebase user server-side
    try:
        firebase_user = firebase_auth.create_user(
            email=body.email,
            display_name=body.display_name or body.email.split("@")[0],
        )
    except firebase_admin.exceptions.AlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create Firebase user: {e}",
        )

    # Check handle uniqueness
    if body.handle:
        handle_check = await db.execute(
            select(Account).where(Account.handle == body.handle)
        )
        if handle_check.scalar_one_or_none():
            # Clean up Firebase user since we can't complete
            try:
                firebase_auth.delete_user(firebase_user.uid)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Handle already taken.",
            )

    # Create account
    account = Account(
        firebase_uid=firebase_user.uid,
        handle=body.handle,
        display_name=body.display_name,
        email=body.email,
    )
    db.add(account)
    await db.flush()

    # Generate API key
    full_key = _generate_key("free")
    key_hash = bcrypt.hashpw(full_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    api_key = ApiKey(
        account_id=account.id,
        key_hash=key_hash,
        key_prefix=full_key[:8],
        tier="free",
        label="onboard",
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(account)

    return OnboardResponse(
        account_id=str(account.id),
        handle=account.handle,
        api_key=full_key,
        gravity_level=account.gravity_level,
        next_level=get_next_level_instructions(account.gravity_level),
    )
