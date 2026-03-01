"""Dual authentication: Firebase ID tokens OR API keys (lp_live_/lp_free_/lp_test_ prefix)."""

from dataclasses import dataclass

import bcrypt
import firebase_admin
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Account, ApiKey

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

security = HTTPBearer(auto_error=False)

API_KEY_PREFIXES = ("lp_live_", "lp_free_", "lp_test_")


@dataclass
class AuthResult:
    account: Account | None
    is_anonymous: bool
    gravity_level: int
    firebase_uid: str | None = None


def _is_api_key(token: str) -> bool:
    return any(token.startswith(p) for p in API_KEY_PREFIXES)


async def _auth_via_api_key(token: str, db: AsyncSession) -> AuthResult:
    """Authenticate via API key (bcrypt hash comparison)."""
    # Find candidate keys by prefix (first 8 chars)
    prefix = token[:8]
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_prefix == prefix,
            ApiKey.revoked_at.is_(None),
        )
    )
    keys = result.scalars().all()

    for key in keys:
        if bcrypt.checkpw(token.encode("utf-8"), key.key_hash.encode("utf-8")):
            # Load the account
            acct_result = await db.execute(
                select(Account).where(Account.id == key.account_id, Account.deleted_at.is_(None))
            )
            account = acct_result.scalar_one_or_none()
            if account:
                return AuthResult(
                    account=account,
                    is_anonymous=False,
                    gravity_level=account.gravity_level,
                )
            break

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


async def _auth_via_firebase(token: str, db: AsyncSession) -> AuthResult:
    """Authenticate via Firebase ID token."""
    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    uid = decoded["uid"]
    result = await db.execute(select(Account).where(Account.firebase_uid == uid, Account.deleted_at.is_(None)))
    account = result.scalar_one_or_none()

    return AuthResult(
        account=account,
        is_anonymous=account is None,
        gravity_level=account.gravity_level if account else 0,
        firebase_uid=uid,
    )


async def authenticate(
    request: Request,
    cred: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Optional auth — returns anonymous AuthResult if no credentials."""
    if cred is None:
        return AuthResult(account=None, is_anonymous=True, gravity_level=0)

    token = cred.credentials
    if _is_api_key(token):
        return await _auth_via_api_key(token, db)
    return await _auth_via_firebase(token, db)


async def require_account(
    request: Request,
    cred: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Mandatory auth — raises 401 if no credentials or no account."""
    if cred is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = cred.credentials
    if _is_api_key(token):
        result = await _auth_via_api_key(token, db)
    else:
        result = await _auth_via_firebase(token, db)

    if result.account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found. Create one first via POST /v1/account",
        )

    return result
