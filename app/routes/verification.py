"""Domain DNS verification + gravity level management."""

import secrets

import dns.resolver
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.database import get_db
from app.models import Account, DomainVerification
from app.schemas import DomainVerifyRequest, DomainVerifyResponse, GravityResponse
from app.services.gravity import (
    compute_gravity_level,
    get_featured_threshold,
    get_gravity_badges,
    get_gravity_multiplier,
    get_next_level_instructions,
)

router = APIRouter(prefix="/v1/account", tags=["verification"])


@router.post("/verify/domain", response_model=DomainVerifyResponse)
async def start_domain_verification(
    body: DomainVerifyRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    domain = body.domain.lower().strip()

    # Generate verification token
    token = f"lightpaper-verify={secrets.token_hex(16)}"

    # Upsert verification record
    result = await db.execute(
        select(DomainVerification).where(
            DomainVerification.account_id == auth.account.id,
            DomainVerification.domain == domain,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.txt_token = token
        existing.verified = False
    else:
        db.add(DomainVerification(
            account_id=auth.account.id,
            domain=domain,
            txt_token=token,
        ))

    await db.commit()

    return DomainVerifyResponse(
        domain=domain,
        txt_record=token,
        instructions=f"Add a TXT record to {domain} with value: {token}\n"
                     f"Then call GET /v1/account/verify/domain/check to confirm.",
    )


@router.get("/verify/domain/check")
async def check_domain_verification(
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DomainVerification).where(
            DomainVerification.account_id == auth.account.id,
            DomainVerification.verified.is_(False),
        )
    )
    pending = result.scalars().all()

    if not pending:
        return {"verified": False, "message": "No pending domain verification. Start one with POST /v1/account/verify/domain"}

    for verification in pending:
        try:
            answers = dns.resolver.resolve(verification.domain, "TXT")
            for rdata in answers:
                txt_value = rdata.to_text().strip('"')
                if txt_value == verification.txt_token:
                    verification.verified = True
                    auth.account.verified_domain = verification.domain
                    # Recompute gravity
                    auth.account.gravity_level = compute_gravity_level(
                        auth.account.verified_domain,
                        auth.account.verified_linkedin,
                        auth.account.orcid_id,
                    )
                    await db.commit()
                    return {
                        "verified": True,
                        "domain": verification.domain,
                        "gravity_level": auth.account.gravity_level,
                    }
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, Exception):
            pass

    return {
        "verified": False,
        "message": "DNS TXT record not found yet. DNS propagation can take up to 48 hours.",
        "domain": pending[0].domain,
        "expected_txt": pending[0].txt_token,
    }


@router.get("/gravity", response_model=GravityResponse)
async def get_gravity(auth: AuthResult = Depends(require_account)):
    account = auth.account
    level = account.gravity_level
    return GravityResponse(
        level=level,
        badges=get_gravity_badges(account.verified_domain, account.verified_linkedin, account.orcid_id),
        next_level=get_next_level_instructions(level),
        multiplier=get_gravity_multiplier(level),
        featured_threshold=get_featured_threshold(level),
    )
