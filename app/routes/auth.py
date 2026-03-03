"""Email OTP + LinkedIn OAuth authentication: /v1/auth/*."""

import hashlib
import hmac
import logging
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Account, ApiKey, Credential, EmailAuthSession, LinkedInAuthSession
from app.rate_limit import limiter
from app.schemas import (
    AuthEmailRequest,
    AuthEmailResponse,
    AuthVerifyRequest,
    AuthVerifyResponse,
    LinkedInAuthPollResponse,
    LinkedInAuthStartResponse,
)
from app.services.api_keys import generate_api_key
from app.services.email import send_otp_email
from app.services.gravity import compute_credential_points, get_next_level_instructions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["auth"])

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


def _mask_email(email: str) -> str:
    """Mask an email: a***@example.com."""
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"


@router.post("/email", response_model=AuthEmailResponse, status_code=200)
@limiter.limit("5/hour")
async def auth_email(
    request: Request,
    body: AuthEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a 6-digit OTP code to the given email. Works for both signup and login."""
    email = body.email.strip().lower()

    # Per-email rate limit: max 3 codes/hour
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    count_result = await db.execute(
        select(func.count())
        .select_from(EmailAuthSession)
        .where(
            func.lower(EmailAuthSession.email) == email,
            EmailAuthSession.created_at >= one_hour_ago,
        )
    )
    recent_count = count_result.scalar() or 0
    if recent_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many codes sent to this email. Try again in an hour.",
        )

    # Generate code + session
    code = str(secrets.randbelow(900000) + 100000)
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    session_id = secrets.token_urlsafe(24)

    session = EmailAuthSession(
        session_id=session_id,
        email=email,
        code_hash=code_hash,
        display_name=body.display_name,
        handle=body.handle,
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )
    db.add(session)
    await db.commit()

    # Send email (best-effort — don't fail the request if Resend is down)
    sent = await send_otp_email(email, code)
    if not sent:
        logger.warning("OTP email delivery failed for session %s", session_id)

    return AuthEmailResponse(
        session_id=session_id,
        message=f"Code sent to {_mask_email(email)}",
        expires_in=600,
    )


@router.post("/verify", response_model=AuthVerifyResponse, status_code=200)
@limiter.limit("10/hour")
async def auth_verify(
    request: Request,
    body: AuthVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify an OTP code. Returns account + API key (creates account if new)."""
    result = await db.execute(
        select(EmailAuthSession).where(EmailAuthSession.session_id == body.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    # Already verified
    if session.verified_at:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Session already used.")

    # Expired
    if datetime.now(UTC) > session.expires_at:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Code expired. Request a new one.")

    # Too many attempts
    if session.attempts >= session.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Request a new code.",
        )

    # Check code
    session.attempts += 1
    code_hash = hashlib.sha256(body.code.encode()).hexdigest()
    if not hmac.compare_digest(code_hash, session.code_hash):
        await db.commit()
        remaining = session.max_attempts - session.attempts
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong code. {remaining} attempt(s) remaining.",
        )

    # Code correct — mark verified
    session.verified_at = datetime.now(UTC)

    # Look up existing account by email
    email = session.email.lower()
    acct_result = await db.execute(
        select(Account).where(
            func.lower(Account.email) == email,
            Account.deleted_at.is_(None),
        )
    )
    account = acct_result.scalar_one_or_none()
    is_new = account is None

    if is_new:
        # Signup: create account
        account = Account(
            firebase_uid=None,
            handle=session.handle,
            display_name=session.display_name or email.split("@")[0],
            email=session.email,
        )
        db.add(account)
        try:
            await db.flush()
        except IntegrityError:
            # Race condition: another request just created this account
            await db.rollback()
            # Re-fetch as login
            session.verified_at = datetime.now(UTC)
            db.add(session)
            acct_result = await db.execute(
                select(Account).where(
                    func.lower(Account.email) == email,
                    Account.deleted_at.is_(None),
                )
            )
            account = acct_result.scalar_one_or_none()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Account creation failed. Please try again.",
                )
            is_new = False

    # Generate API key (auto-revoke any existing email_auth-labeled key)
    if not is_new:
        existing_keys = await db.execute(
            select(ApiKey).where(
                ApiKey.account_id == account.id,
                ApiKey.label == "email_auth",
                ApiKey.revoked_at.is_(None),
            )
        )
        for old_key in existing_keys.scalars().all():
            old_key.revoked_at = datetime.now(UTC)

    full_key, key_hash, key_prefix = generate_api_key(account.tier)
    api_key = ApiKey(
        account_id=account.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        tier=account.tier,
        label="email_auth",
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(account)

    return AuthVerifyResponse(
        account_id=str(account.id),
        handle=account.handle,
        api_key=full_key,
        is_new_account=is_new,
        gravity_level=account.gravity_level,
        next_level=get_next_level_instructions(
            account.gravity_level,
            verified_domain=account.verified_domain,
            verified_linkedin=account.verified_linkedin,
            orcid_id=account.orcid_id,
            credential_points=compute_credential_points(
                (await db.execute(
                    select(Credential).where(Credential.account_id == account.id)
                )).scalars().all()
            ),
        ),
    )


@router.post("/linkedin", response_model=LinkedInAuthStartResponse, status_code=200)
@limiter.limit("10/hour")
async def auth_linkedin(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Start LinkedIn OAuth for login/signup. Returns an authorization URL."""
    if not settings.linkedin_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn authentication is not configured.",
        )

    session_id = secrets.token_urlsafe(24)
    state_token = secrets.token_urlsafe(32)

    session = LinkedInAuthSession(
        session_id=session_id,
        state_token=state_token,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db.add(session)
    await db.commit()

    redirect_uri = f"{settings.base_url}/v1/auth/linkedin/callback"
    params = {
        "response_type": "code",
        "client_id": settings.linkedin_client_id,
        "redirect_uri": redirect_uri,
        "state": state_token,
        "scope": "openid profile email",
    }
    authorization_url = f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"

    return LinkedInAuthStartResponse(
        authorization_url=authorization_url,
        session_id=session_id,
        instructions="Open this URL in your browser to sign in with LinkedIn.",
    )


@router.get("/linkedin/callback", response_class=HTMLResponse)
@limiter.limit("10/hour")
async def auth_linkedin_callback(
    request: Request,
    code: str = "",
    state: str = "",
    error: str = "",
    db: AsyncSession = Depends(get_db),
):
    """LinkedIn OAuth callback. Matches or creates an account, stores API key for poll pickup."""
    if error:
        return HTMLResponse(
            content=_result_page("Authentication Failed", f"LinkedIn returned an error: {error}"),
            status_code=400,
        )

    if not code or not state:
        return HTMLResponse(
            content=_result_page("Authentication Failed", "Missing authorization code or state."),
            status_code=400,
        )

    # Look up session by state token
    result = await db.execute(
        select(LinkedInAuthSession).where(
            LinkedInAuthSession.state_token == state,
            LinkedInAuthSession.completed_at.is_(None),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        return HTMLResponse(
            content=_result_page("Authentication Failed", "Invalid or expired state token."),
            status_code=400,
        )

    if datetime.now(UTC) > session.expires_at:
        return HTMLResponse(
            content=_result_page("Authentication Failed", "Session expired. Please start again."),
            status_code=400,
        )

    # Exchange code for access token
    redirect_uri = f"{settings.base_url}/v1/auth/linkedin/callback"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_resp = await client.post(
                LINKEDIN_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": settings.linkedin_client_id,
                    "client_secret": settings.linkedin_client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if token_resp.status_code != 200:
                return HTMLResponse(
                    content=_result_page("Authentication Failed", "Could not exchange authorization code."),
                    status_code=400,
                )

            token_data = token_resp.json()
            access_token = token_data["access_token"]

            # Fetch profile
            profile_resp = await client.get(
                LINKEDIN_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_resp.status_code != 200:
                return HTMLResponse(
                    content=_result_page("Authentication Failed", "Could not fetch LinkedIn profile."),
                    status_code=400,
                )

            profile = profile_resp.json()
    except httpx.HTTPError:
        return HTMLResponse(
            content=_result_page("Authentication Failed", "Network error contacting LinkedIn."),
            status_code=502,
        )

    linkedin_sub = profile.get("sub", "")
    linkedin_email = profile.get("email", "")
    linkedin_name = profile.get("name", "")

    # Match account: first by linkedin_profile_id, then by email
    account = None
    is_new = False

    if linkedin_sub:
        acct_result = await db.execute(
            select(Account).where(
                Account.linkedin_profile_id == linkedin_sub,
                Account.deleted_at.is_(None),
            )
        )
        account = acct_result.scalar_one_or_none()

    if not account and linkedin_email:
        acct_result = await db.execute(
            select(Account).where(
                func.lower(Account.email) == linkedin_email.lower(),
                Account.deleted_at.is_(None),
            )
        )
        account = acct_result.scalar_one_or_none()

    if not account:
        # Create new account from LinkedIn profile
        account = Account(
            firebase_uid=None,
            display_name=linkedin_name or (linkedin_email.split("@")[0] if linkedin_email else "LinkedIn User"),
            email=linkedin_email or None,
            linkedin_profile_id=linkedin_sub or None,
            verified_linkedin=True,
        )
        db.add(account)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            # Re-fetch by email (race condition)
            if linkedin_email:
                acct_result = await db.execute(
                    select(Account).where(
                        func.lower(Account.email) == linkedin_email.lower(),
                        Account.deleted_at.is_(None),
                    )
                )
                account = acct_result.scalar_one_or_none()
            if not account:
                return HTMLResponse(
                    content=_result_page("Authentication Failed", "Account creation failed. Please try again."),
                    status_code=500,
                )
        else:
            is_new = True

    # Ensure LinkedIn profile data is stored on account
    if linkedin_sub and not account.linkedin_profile_id:
        account.linkedin_profile_id = linkedin_sub
    if not account.verified_linkedin:
        account.verified_linkedin = True

    # Generate API key
    full_key, key_hash, key_prefix = generate_api_key(account.tier)
    api_key = ApiKey(
        account_id=account.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        tier=account.tier,
        label="linkedin_auth",
    )
    db.add(api_key)

    # Store key in session for poll pickup
    session.account_id = account.id
    session.api_key_plain = full_key
    session.completed_at = datetime.now(UTC)

    await db.commit()

    status_text = "account created" if is_new else "signed in"
    name = linkedin_name or "your LinkedIn account"
    return HTMLResponse(
        content=_result_page(
            "Signed In",
            f"Successfully {status_text} as {name}. You can close this tab.",
        ),
    )


@router.get("/linkedin/poll", response_model=LinkedInAuthPollResponse, status_code=200)
@limiter.limit("60/hour")
async def auth_linkedin_poll(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Poll for LinkedIn OAuth completion. Returns API key on first read, then nulls it."""
    result = await db.execute(
        select(LinkedInAuthSession).where(LinkedInAuthSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    if datetime.now(UTC) > session.expires_at:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Session expired.")

    if not session.completed_at:
        return LinkedInAuthPollResponse(completed=False)

    # Load account for response
    acct_result = await db.execute(select(Account).where(Account.id == session.account_id))
    account = acct_result.scalar_one_or_none()

    # One-time read: return api_key then null it
    api_key = session.api_key_plain
    if session.api_key_plain:
        session.api_key_plain = None
        await db.commit()

    return LinkedInAuthPollResponse(
        completed=True,
        account_id=str(account.id) if account else None,
        handle=account.handle if account else None,
        api_key=api_key,
        gravity_level=account.gravity_level if account else None,
    )


def _result_page(title: str, message: str) -> str:
    """Simple HTML result page for OAuth callback."""
    from html import escape

    t = escape(title)
    m = escape(message)
    return f"""<!DOCTYPE html>
<html><head><title>{t} — lightpaper.org</title>
<style>body{{font-family:system-ui,sans-serif;max-width:480px;margin:80px auto;text-align:center}}
h1{{font-size:1.5rem}}p{{color:#555}}</style></head>
<body><h1>{t}</h1><p>{m}</p></body></html>"""
