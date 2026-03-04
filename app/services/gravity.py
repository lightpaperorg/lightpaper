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


def _count_identities(
    verified_domain: str | None,
    verified_linkedin: bool,
    orcid_id: str | None,
) -> int:
    """Count independent identity verifications (0-3)."""
    return sum([bool(verified_domain), bool(verified_linkedin), bool(orcid_id)])


def compute_gravity_level(
    verified_domain: str | None,
    verified_linkedin: bool,
    orcid_id: str | None,
    credentials: list[Credential] | None = None,
) -> int:
    """Compute gravity level 0-5 from independent verifications + credentials.

    Non-hierarchical: any combination of identity verifications and credential
    points can reach any level. No single verification is a prerequisite.

    | Level | Requirement                                            |
    |-------|--------------------------------------------------------|
    | 0     | Nothing                                                |
    | 1     | Any 1 identity verification                            |
    | 2     | 2 identities                                           |
    | 3     | 3 identities, OR 2 ids + cred_pts >= 1, OR 1 id + cred_pts >= 3 |
    | 4     | 2+ ids + cred_pts >= 3, OR 1 id + cred_pts >= 6       |
    | 5     | 2+ ids + cred_pts >= 6                                 |
    """
    ids = _count_identities(verified_domain, verified_linkedin, orcid_id)
    pts = compute_credential_points(credentials)

    # Credentials without at least one identity verification don't count
    if ids == 0:
        return 0

    # Level 5: 2+ ids + 6+ pts
    if ids >= 2 and pts >= 6:
        return 5

    # Level 4: 2+ ids + 3+ pts, OR 1 id + 6+ pts
    if (ids >= 2 and pts >= 3) or (ids >= 1 and pts >= 6):
        return 4

    # Level 3: 3 ids, OR 2 ids + 1+ pts, OR 1 id + 3+ pts
    if ids >= 3 or (ids >= 2 and pts >= 1) or (ids >= 1 and pts >= 3):
        return 3

    # Level 2: 2 ids
    if ids >= 2:
        return 2

    # Level 1: 1 id
    return 1


def get_gravity_multiplier(level: int) -> float:
    return GRAVITY_MULTIPLIERS.get(level, 1.0)


def get_featured_threshold(level: int) -> int:
    return FEATURED_THRESHOLDS.get(level, 70)


_DEGREE_ABBREV = {
    "Bachelor of Science": "BSc",
    "Bachelor of Arts": "BA",
    "Bachelor of Applied Science": "BASc",
    "Bachelor of Engineering": "BEng",
    "Bachelor of Commerce": "BCom",
    "Master of Science": "MSc",
    "Master of Arts": "MA",
    "Master of Business Administration": "MBA",
    "Master of Engineering": "MEng",
    "Doctor of Philosophy": "PhD",
    "Graduate Diploma": "GradDip",
    "Graduate Certificate": "GradCert",
}


def _abbreviate_title(title: str) -> str:
    """Abbreviate common degree prefixes: 'Bachelor of Science (Physics)' → 'BSc (Physics)'."""
    for full, abbrev in _DEGREE_ABBREV.items():
        if title.startswith(full):
            remainder = title[len(full):]
            return f"{abbrev}{remainder}" if remainder else abbrev
    return title


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
            short_title = _abbreviate_title(c.title)
            badge = f"{short_title} \u00b7 {c.institution} {tier_label.get(c.evidence_tier, '')}"
            badges.append(badge)
    return badges


def is_featured_eligible(quality_score: int, gravity_level: int) -> bool:
    threshold = get_featured_threshold(gravity_level)
    return quality_score >= threshold


def compute_ranking_score(quality_score: int, gravity_level: int, ts_rank: float = 1.0) -> float:
    """Compute search ranking score: ts_rank x quality x gravity multiplier."""
    multiplier = get_gravity_multiplier(gravity_level)
    return ts_rank * quality_score * multiplier


def get_next_level_instructions(
    level: int,
    verified_domain: str | None = None,
    verified_linkedin: bool = False,
    orcid_id: str | None = None,
    credential_points: int = 0,
) -> str | None:
    """Return context-sensitive instructions for reaching the next gravity level."""
    if level >= 5:
        return None

    # Collect missing identity verifications
    missing: list[str] = []
    if not verified_domain:
        missing.append("verify your domain via DNS TXT record (POST /v1/account/verify/domain)")
    if not verified_linkedin:
        missing.append("connect LinkedIn (POST /v1/account/verify/linkedin)")
    if not orcid_id:
        missing.append("link your ORCID iD (POST /v1/account/verify/orcid)")

    ids = _count_identities(verified_domain, verified_linkedin, orcid_id)
    target = level + 1
    target_mult = GRAVITY_MULTIPLIERS.get(target, 1.0)
    boost = f"Level {target} ({target_mult}x search boost)"

    if level == 0:
        # Need any one identity
        return f"To reach {boost}: {missing[0]}" if missing else None

    if level == 1:
        # Need: 2 ids, or 1 id + 3 cred pts → level 2 or jump to 3
        parts = []
        if missing:
            parts.append(missing[0])
        if credential_points < 3:
            parts.append("submit verified credentials (POST /v1/account/credentials)")
        if parts:
            return f"To reach {boost}: {parts[0]}"
        return None

    if level == 2:
        # Need: 3 ids, or 2 ids + 1 cred pt, or 1 id + 3 cred pts
        parts = []
        if missing:
            parts.append(missing[0])
        if credential_points < 1:
            parts.append("submit verified credentials (POST /v1/account/credentials)")
        if parts:
            return f"To reach {boost}: {parts[0]}"
        return None

    if level == 3:
        # Need: 2+ ids + 3 pts, or 1 id + 6 pts
        parts = []
        if ids < 2 and missing:
            parts.append(missing[0])
        if credential_points < 3:
            needed = 3 - credential_points
            parts.append(f"earn {needed} more credential point(s) (POST /v1/account/credentials)")
        if parts:
            return f"To reach {boost}: {', and '.join(parts)}"
        return None

    if level == 4:
        # Need: 2+ ids + 6 pts
        parts = []
        if ids < 2 and missing:
            parts.append(missing[0])
        if credential_points < 6:
            needed = 6 - credential_points
            parts.append(f"earn {needed} more credential point(s) (POST /v1/account/credentials)")
        if parts:
            return f"To reach {boost}: {', and '.join(parts)}"
        return None

    return None
