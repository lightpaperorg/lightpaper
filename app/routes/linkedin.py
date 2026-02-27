"""LinkedIn OAuth verification: start, callback, check."""

import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.config import settings
from app.database import get_db
from app.models import Account, Document, LinkedInVerification
from app.rate_limit import limiter
from app.schemas import LinkedInCheckResponse, LinkedInVerifyResponse
from app.services.gravity import compute_gravity_level

router = APIRouter(prefix="/v1/account", tags=["verification"])

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


@router.post("/verify/linkedin", response_model=LinkedInVerifyResponse)
@limiter.limit("10/hour")
async def start_linkedin_verification(
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Start LinkedIn OAuth flow. Returns an authorization URL for the pilot to open."""
    if not settings.linkedin_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn verification is not configured.",
        )

    if auth.account.verified_linkedin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="LinkedIn already verified.",
        )

    # Generate state token
    state = secrets.token_urlsafe(32)

    # Store verification record
    verification = LinkedInVerification(
        account_id=auth.account.id,
        state_token=state,
    )
    db.add(verification)
    await db.commit()

    # Build authorization URL
    redirect_uri = f"{settings.base_url}/v1/account/verify/linkedin/callback"
    params = {
        "response_type": "code",
        "client_id": settings.linkedin_client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "openid profile",
    }
    authorization_url = f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"

    return LinkedInVerifyResponse(
        authorization_url=authorization_url,
        state=state,
        instructions="Open this URL in your browser to verify your LinkedIn identity.",
    )


@router.get("/verify/linkedin/callback", response_class=HTMLResponse)
async def linkedin_callback(
    request: Request,
    code: str = "",
    state: str = "",
    error: str = "",
    db: AsyncSession = Depends(get_db),
):
    """LinkedIn OAuth callback. Exchanges code for token and verifies identity."""
    if error:
        return HTMLResponse(
            content=_result_page("Verification Failed", f"LinkedIn returned an error: {error}"),
            status_code=400,
        )

    if not code or not state:
        return HTMLResponse(
            content=_result_page("Verification Failed", "Missing authorization code or state."),
            status_code=400,
        )

    # Look up verification by state token
    result = await db.execute(
        select(LinkedInVerification).where(
            LinkedInVerification.state_token == state,
            LinkedInVerification.verified.is_(False),
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        return HTMLResponse(
            content=_result_page("Verification Failed", "Invalid or expired state token."),
            status_code=400,
        )

    # Load the account
    acct_result = await db.execute(
        select(Account).where(Account.id == verification.account_id)
    )
    account = acct_result.scalar_one_or_none()
    if not account:
        return HTMLResponse(
            content=_result_page("Verification Failed", "Account not found."),
            status_code=400,
        )

    # Exchange code for access token
    redirect_uri = f"{settings.base_url}/v1/account/verify/linkedin/callback"
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
                    content=_result_page("Verification Failed", "Could not exchange authorization code."),
                    status_code=400,
                )

            token_data = token_resp.json()
            access_token = token_data["access_token"]

            # Fetch profile to confirm identity
            profile_resp = await client.get(
                LINKEDIN_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_resp.status_code != 200:
                return HTMLResponse(
                    content=_result_page("Verification Failed", "Could not fetch LinkedIn profile."),
                    status_code=400,
                )

            profile = profile_resp.json()
    except httpx.HTTPError:
        return HTMLResponse(
            content=_result_page("Verification Failed", "Network error contacting LinkedIn."),
            status_code=502,
        )

    # Mark verified + propagate to documents
    verification.verified = True
    verification.linkedin_profile_id = profile.get("sub", "")
    account.verified_linkedin = True
    account.gravity_level = compute_gravity_level(
        account.verified_domain,
        account.verified_linkedin,
        account.orcid_id,
    )
    await db.execute(
        update(Document)
        .where(Document.account_id == account.id, Document.deleted_at.is_(None))
        .values(author_gravity=account.gravity_level)
    )
    await db.commit()

    name = profile.get("name", "your LinkedIn account")
    return HTMLResponse(
        content=_result_page(
            "LinkedIn Verified",
            f"Successfully linked {name}. Your gravity level is now {account.gravity_level}. You can close this tab.",
        ),
    )


@router.get("/verify/linkedin/check", response_model=LinkedInCheckResponse)
async def check_linkedin_verification(
    auth: AuthResult = Depends(require_account),
):
    """Poll endpoint for agents to check if LinkedIn OAuth was completed."""
    return LinkedInCheckResponse(
        verified=auth.account.verified_linkedin,
        gravity_level=auth.account.gravity_level,
    )


def _result_page(title: str, message: str) -> str:
    """Simple HTML result page for OAuth callback."""
    return f"""<!DOCTYPE html>
<html><head><title>{title} — lightpaper.org</title>
<style>body{{font-family:system-ui,sans-serif;max-width:480px;margin:80px auto;text-align:center}}
h1{{font-size:1.5rem}}p{{color:#555}}</style></head>
<body><h1>{title}</h1><p>{message}</p></body></html>"""
