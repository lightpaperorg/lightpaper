"""Domain DNS verification, ORCID verification, gravity level management."""

import secrets

import dns.resolver
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import update

from app.auth import AuthResult, require_account
from app.database import get_db
from app.models import Account, Credential, Document, DomainVerification
from app.rate_limit import limiter
from app.schemas import (
    DomainVerifyRequest,
    DomainVerifyResponse,
    GravityResponse,
    OrcidVerifyRequest,
    OrcidVerifyResponse,
)
from app.services.gravity import (
    compute_gravity_level,
    get_featured_threshold,
    get_gravity_badges,
    get_gravity_multiplier,
    get_next_level_instructions,
)

async def _load_credentials(account_id, db: AsyncSession) -> list:
    result = await db.execute(select(Credential).where(Credential.account_id == account_id))
    return result.scalars().all()

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
                    # Recompute gravity + propagate to documents
                    creds = await _load_credentials(auth.account.id, db)
                    auth.account.gravity_level = compute_gravity_level(
                        auth.account.verified_domain,
                        auth.account.verified_linkedin,
                        auth.account.orcid_id,
                        credentials=creds,
                    )
                    await db.execute(
                        update(Document)
                        .where(Document.account_id == auth.account.id, Document.deleted_at.is_(None))
                        .values(author_gravity=auth.account.gravity_level)
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


@router.post("/verify/orcid", response_model=OrcidVerifyResponse)
@limiter.limit("10/hour")
async def verify_orcid(
    request: Request,
    body: OrcidVerifyRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Verify ORCID iD via the public ORCID API. Fully agent-automatable."""
    if auth.account.orcid_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ORCID already verified.",
        )

    # Validate against ORCID public API
    orcid_name = None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://pub.orcid.org/v3.0/{body.orcid_id}",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"ORCID iD {body.orcid_id} not found.",
                )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Could not validate ORCID iD with ORCID.org.",
                )
            data = resp.json()
            # Extract name from ORCID response
            person = data.get("person", {})
            name_obj = person.get("name", {})
            given = name_obj.get("given-names", {}).get("value", "")
            family = name_obj.get("family-name", {}).get("value", "")
            if given or family:
                orcid_name = f"{given} {family}".strip()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Network error contacting ORCID.org.",
        )

    # Check that this ORCID isn't already claimed by another account
    existing = await db.execute(
        select(Account).where(Account.orcid_id == body.orcid_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This ORCID iD is already linked to another account.",
        )

    # Update account + propagate to documents
    auth.account.orcid_id = body.orcid_id
    creds = await _load_credentials(auth.account.id, db)
    auth.account.gravity_level = compute_gravity_level(
        auth.account.verified_domain,
        auth.account.verified_linkedin,
        auth.account.orcid_id,
        credentials=creds,
    )
    await db.execute(
        update(Document)
        .where(Document.account_id == auth.account.id, Document.deleted_at.is_(None))
        .values(author_gravity=auth.account.gravity_level)
    )
    await db.commit()

    return OrcidVerifyResponse(
        verified=True,
        gravity_level=auth.account.gravity_level,
        orcid_name=orcid_name,
    )


@router.get("/gravity", response_model=GravityResponse)
async def get_gravity(
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    account = auth.account
    creds = await _load_credentials(account.id, db)
    level = account.gravity_level
    return GravityResponse(
        level=level,
        badges=get_gravity_badges(account.verified_domain, account.verified_linkedin, account.orcid_id, credentials=creds),
        next_level=get_next_level_instructions(level),
        multiplier=get_gravity_multiplier(level),
        featured_threshold=get_featured_threshold(level),
    )
