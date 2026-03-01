"""Author Gravity: verification levels, multipliers, badges."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Credential

GRAVITY_MULTIPLIERS = {0: 1.0, 1: 1.1, 2: 1.25, 3: 1.4, 4: 1.55, 5: 1.7}
FEATURED_THRESHOLDS = {0: 70, 1: 68, 2: 65, 3: 60, 4: 57, 5: 55}

EVIDENCE_TIER_POINTS = {"confirmed": 3, "supported": 2, "claimed": 1}

# Credential points required for levels 4 and 5
CREDENTIAL_LEVEL_THRESHOLDS = {4: 3, 5: 6}


def compute_credential_points(credentials: list[Credential] | None) -> int:
    """Sum points from credential evidence tiers."""
    if not credentials:
        return 0
    return sum(EVIDENCE_TIER_POINTS.get(c.evidence_tier, 0) for c in credentials)


def compute_gravity_level(
    verified_domain: str | None,
    verified_linkedin: bool,
    orcid_id: str | None,
    credentials: list[Credential] | None = None,
) -> int:
    """Compute gravity level 0-5 from verification fields + credentials."""
    # Base level 0-3 from identity verifications
    if verified_domain and verified_linkedin and orcid_id:
        base = 3
    elif verified_domain and verified_linkedin:
        base = 2
    elif verified_domain:
        base = 1
    else:
        base = 0

    # Credential points can push to levels 4-5 (requires base level 3)
    if base >= 3 and credentials:
        points = compute_credential_points(credentials)
        if points >= CREDENTIAL_LEVEL_THRESHOLDS[5]:
            return 5
        if points >= CREDENTIAL_LEVEL_THRESHOLDS[4]:
            return 4

    return base


def get_gravity_multiplier(level: int) -> float:
    return GRAVITY_MULTIPLIERS.get(level, 1.0)


def get_featured_threshold(level: int) -> int:
    return FEATURED_THRESHOLDS.get(level, 70)


def get_gravity_badges(
    verified_domain: str | None,
    verified_linkedin: bool,
    orcid_id: str | None,
    credentials: list[Credential] | None = None,
) -> list[str]:
    """Return list of verification badges."""
    badges = []
    if verified_domain:
        badges.append(f"{verified_domain} \u2713")
    if verified_linkedin:
        badges.append("LinkedIn \u2713")
    if orcid_id:
        badges.append(f"ORCID {orcid_id} \u2713")
    if credentials:
        for c in credentials:
            tier_label = {"confirmed": "\u2713\u2713", "supported": "\u2713", "claimed": "\u00b7"}
            badge = f"{c.institution} {tier_label.get(c.evidence_tier, '')}"
            badges.append(badge)
    return badges


def is_featured_eligible(quality_score: int, gravity_level: int) -> bool:
    threshold = get_featured_threshold(gravity_level)
    return quality_score >= threshold


def compute_ranking_score(quality_score: int, gravity_level: int, ts_rank: float = 1.0) -> float:
    """Compute search ranking score: ts_rank x quality x gravity multiplier."""
    multiplier = get_gravity_multiplier(gravity_level)
    return ts_rank * quality_score * multiplier


def get_next_level_instructions(level: int) -> str | None:
    """Return instructions for reaching the next gravity level."""
    if level == 0:
        return "Verify your domain via DNS TXT record to reach Level 1 (1.1x search boost)"
    if level == 1:
        return "Connect LinkedIn to reach Level 2 (1.25x search boost)"
    if level == 2:
        return "Link your ORCID iD to reach Level 3 (1.4x search boost)"
    if level == 3:
        return "Submit verified credentials to reach Level 4 (1.55x search boost). Use POST /v1/account/credentials"
    if level == 4:
        return "Submit more verified credentials to reach Level 5 (1.7x search boost). Need 6 credential points total"
    return None
