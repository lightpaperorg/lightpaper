"""Author Gravity: verification levels, multipliers, badges."""

GRAVITY_MULTIPLIERS = {0: 1.0, 1: 1.1, 2: 1.25, 3: 1.4}
FEATURED_THRESHOLDS = {0: 70, 1: 68, 2: 65, 3: 60}


def compute_gravity_level(
    verified_domain: str | None,
    verified_linkedin: bool,
    orcid_id: str | None,
) -> int:
    """Compute gravity level 0-3 from verification fields."""
    if verified_domain and verified_linkedin and orcid_id:
        return 3
    if verified_domain and verified_linkedin:
        return 2
    if verified_domain:
        return 1
    return 0


def get_gravity_multiplier(level: int) -> float:
    return GRAVITY_MULTIPLIERS.get(level, 1.0)


def get_featured_threshold(level: int) -> int:
    return FEATURED_THRESHOLDS.get(level, 70)


def get_gravity_badges(
    verified_domain: str | None,
    verified_linkedin: bool,
    orcid_id: str | None,
) -> list[str]:
    """Return list of verification badges."""
    badges = []
    if verified_domain:
        badges.append(f"{verified_domain} \u2713")
    if verified_linkedin:
        badges.append("LinkedIn \u2713")
    if orcid_id:
        badges.append(f"ORCID {orcid_id} \u2713")
    return badges


def is_featured_eligible(quality_score: int, gravity_level: int) -> bool:
    threshold = get_featured_threshold(gravity_level)
    return quality_score >= threshold


def compute_ranking_score(quality_score: int, gravity_level: int, ts_rank: float = 1.0) -> float:
    """Compute search ranking score: ts_rank × quality × gravity multiplier."""
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
    return None
