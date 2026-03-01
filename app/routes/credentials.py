"""POST/GET /v1/account/credentials — agent-driven credential verification."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.database import get_db
from app.models import Credential, Document
from app.rate_limit import limiter
from app.schemas import (
    CredentialResponse,
    CredentialSubmitRequest,
    CredentialSubmitResponse,
)
from app.services.gravity import (
    compute_credential_points,
    compute_gravity_level,
    get_gravity_badges,
)

router = APIRouter(prefix="/v1/account", tags=["credentials"])

TIER_RANK = {"claimed": 0, "supported": 1, "confirmed": 2}


@router.post("/credentials", response_model=CredentialSubmitResponse)
@limiter.limit("20/hour")
async def submit_credentials(
    request: Request,
    body: CredentialSubmitRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Batch upsert credentials. Only upgrades evidence tiers, never downgrades."""
    account = auth.account

    for sub in body.credentials:
        # Check for existing credential (same type + institution + title)
        result = await db.execute(
            select(Credential).where(
                Credential.account_id == account.id,
                Credential.credential_type == sub.credential_type,
                Credential.institution == sub.institution,
                Credential.title == sub.title,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Only upgrade tier, never downgrade
            if TIER_RANK.get(sub.evidence_tier, 0) > TIER_RANK.get(existing.evidence_tier, 0):
                existing.evidence_tier = sub.evidence_tier
                existing.evidence_data = sub.evidence_data
                existing.agent_notes = sub.agent_notes
                existing.year = sub.year or existing.year
                existing.updated_at = datetime.now(UTC)
        else:
            db.add(
                Credential(
                    account_id=account.id,
                    credential_type=sub.credential_type,
                    institution=sub.institution,
                    title=sub.title,
                    year=sub.year,
                    evidence_tier=sub.evidence_tier,
                    evidence_data=sub.evidence_data,
                    agent_notes=sub.agent_notes,
                )
            )

    await db.flush()

    # Reload all credentials for this account
    cred_result = await db.execute(select(Credential).where(Credential.account_id == account.id))
    all_creds = cred_result.scalars().all()

    # Recompute gravity
    new_level = compute_gravity_level(
        account.verified_domain,
        account.verified_linkedin,
        account.orcid_id,
        credentials=all_creds,
    )
    account.gravity_level = new_level

    # Propagate to documents
    await db.execute(
        update(Document)
        .where(Document.account_id == account.id, Document.deleted_at.is_(None))
        .values(author_gravity=new_level)
    )

    await db.commit()

    cred_responses = [
        CredentialResponse(
            id=str(c.id),
            credential_type=c.credential_type,
            institution=c.institution,
            title=c.title,
            year=c.year,
            evidence_tier=c.evidence_tier,
            agent_notes=c.agent_notes,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in all_creds
    ]

    return CredentialSubmitResponse(
        credentials=cred_responses,
        gravity_level=new_level,
        gravity_badges=get_gravity_badges(
            account.verified_domain,
            account.verified_linkedin,
            account.orcid_id,
            credentials=all_creds,
        ),
        credential_points=compute_credential_points(all_creds),
    )


@router.get("/credentials", response_model=list[CredentialResponse])
async def list_credentials(
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """List all credentials for the authenticated account."""
    result = await db.execute(
        select(Credential).where(Credential.account_id == auth.account.id).order_by(Credential.created_at.desc())
    )
    creds = result.scalars().all()

    return [
        CredentialResponse(
            id=str(c.id),
            credential_type=c.credential_type,
            institution=c.institution,
            title=c.title,
            year=c.year,
            evidence_tier=c.evidence_tier,
            agent_notes=c.agent_notes,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in creds
    ]
