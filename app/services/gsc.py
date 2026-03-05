"""Google Search Console URL Inspection API integration."""

import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Document

logger = logging.getLogger(__name__)

INSPECTION_API_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _get_credentials():
    """Build Google credentials from service account key JSON."""
    if not settings.gsc_service_account_key:
        return None
    try:
        from google.oauth2.service_account import Credentials

        info = json.loads(settings.gsc_service_account_key)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    except Exception:
        logger.warning("Failed to load GSC service account credentials", exc_info=True)
        return None


async def inspect_url(url: str) -> dict | None:
    """Inspect a single URL via the Search Console URL Inspection API.

    Returns parsed inspection result or None on error.
    """
    credentials = _get_credentials()
    if credentials is None:
        return None

    # Refresh the token synchronously (google-auth doesn't have async refresh)
    from google.auth.transport.requests import Request as GoogleAuthRequest

    credentials.refresh(GoogleAuthRequest())

    payload = {
        "inspectionUrl": url,
        "siteUrl": "sc-domain:lightpaper.org",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                INSPECTION_API_URL,
                json=payload,
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
            if resp.status_code != 200:
                logger.warning("URL Inspection API %s for %s: %s", resp.status_code, url, resp.text)
                return None
            return resp.json()
    except Exception:
        logger.warning("URL Inspection API call failed for %s", url, exc_info=True)
        return None


async def check_indexing_batch(db: AsyncSession, limit: int = 100) -> dict:
    """Check indexing status for documents needing a refresh.

    Queries documents that are listed, quality >= 40, and either never checked
    or not checked in the last 24 hours. Updates DB columns with results.

    Returns a summary report.
    """
    if not settings.gsc_service_account_key:
        return {"error": "GSC service account not configured", "configured": False}

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    result = await db.execute(
        select(Document)
        .where(
            Document.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.quality_score >= 40,
            (Document.google_index_checked_at.is_(None))
            | (Document.google_index_checked_at < cutoff),
        )
        .order_by(Document.google_index_checked_at.asc().nullsfirst())
        .limit(limit)
    )
    docs = result.scalars().all()

    checked = 0
    errors = 0
    for doc in docs:
        url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"
        inspection = await inspect_url(url)

        if inspection is None:
            errors += 1
            continue

        # Parse the inspection result
        index_result = inspection.get("inspectionResult", {}).get("indexStatusResult", {})
        coverage_state = index_result.get("coverageState", "UNKNOWN")
        verdict = index_result.get("verdict", "UNKNOWN")

        doc.google_indexed = verdict == "PASS"
        doc.google_coverage_state = coverage_state
        doc.google_index_checked_at = datetime.now(timezone.utc)
        checked += 1

    if checked > 0:
        await db.commit()

    # Build full report from all listed documents
    all_result = await db.execute(
        select(Document)
        .where(
            Document.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.quality_score >= 40,
        )
        .order_by(Document.created_at.desc())
    )
    all_docs = all_result.scalars().all()

    indexed = []
    not_indexed = []
    unchecked = []
    for doc in all_docs:
        doc_url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"
        info = {
            "id": doc.id,
            "title": doc.title,
            "url": doc_url,
            "quality_score": doc.quality_score,
            "coverage_state": doc.google_coverage_state,
            "last_checked": doc.google_index_checked_at.isoformat() if doc.google_index_checked_at else None,
        }
        if doc.google_index_checked_at is None:
            unchecked.append(info)
        elif doc.google_indexed:
            indexed.append(info)
        else:
            not_indexed.append(info)

    return {
        "configured": True,
        "total_documents": len(all_docs),
        "indexed": len(indexed),
        "not_indexed": len(not_indexed),
        "unchecked": len(unchecked),
        "just_checked": checked,
        "check_errors": errors,
        "indexed_documents": indexed,
        "not_indexed_documents": not_indexed,
        "unchecked_documents": unchecked,
    }
