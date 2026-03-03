"""Test non-hierarchical gravity computation. No database needed."""

from dataclasses import dataclass

from app.services.gravity import (
    GRAVITY_MULTIPLIERS,
    compute_credential_points,
    compute_gravity_level,
    get_next_level_instructions,
)


@dataclass
class FakeCredential:
    """Minimal credential stand-in for testing."""

    evidence_tier: str
    institution: str = "Test University"


def _creds(*tiers: str) -> list[FakeCredential]:
    return [FakeCredential(evidence_tier=t) for t in tiers]


# ---------------------------------------------------------------------------
# Level 0: no verifications
# ---------------------------------------------------------------------------


class TestLevel0:
    def test_no_verifications(self):
        assert compute_gravity_level(None, False, None) == 0

    def test_credentials_without_identity_ignored(self):
        """Credentials alone don't count — need at least 1 identity."""
        assert compute_gravity_level(None, False, None, _creds("confirmed", "confirmed")) == 0

    def test_empty_credential_list(self):
        assert compute_gravity_level(None, False, None, []) == 0


# ---------------------------------------------------------------------------
# Level 1: any 1 identity verification
# ---------------------------------------------------------------------------


class TestLevel1:
    def test_domain_only(self):
        assert compute_gravity_level("example.com", False, None) == 1

    def test_linkedin_only(self):
        assert compute_gravity_level(None, True, None) == 1

    def test_orcid_only(self):
        assert compute_gravity_level(None, False, "0000-0001-2345-6789") == 1


# ---------------------------------------------------------------------------
# Level 2: 2 identity verifications
# ---------------------------------------------------------------------------


class TestLevel2:
    def test_domain_and_linkedin(self):
        assert compute_gravity_level("example.com", True, None) == 2

    def test_domain_and_orcid(self):
        assert compute_gravity_level("example.com", False, "0000-0001-2345-6789") == 2

    def test_linkedin_and_orcid(self):
        assert compute_gravity_level(None, True, "0000-0001-2345-6789") == 2


# ---------------------------------------------------------------------------
# Level 3: 3 ids, OR 2 ids + 1 cred pt, OR 1 id + 3 cred pts
# ---------------------------------------------------------------------------


class TestLevel3:
    def test_all_three_identities(self):
        assert compute_gravity_level("example.com", True, "0000-0001-2345-6789") == 3

    def test_two_ids_plus_claimed(self):
        """2 identities + 1 claimed credential point."""
        assert compute_gravity_level("example.com", True, None, _creds("claimed")) == 3

    def test_two_ids_plus_supported(self):
        """2 identities + 2 supported points → still level 3 (< 3 pts for level 4)."""
        assert compute_gravity_level(None, True, "0000-0001-2345-6789", _creds("supported")) == 3

    def test_linkedin_plus_confirmed_degree(self):
        """THE KEY USER CASE: LinkedIn + confirmed degree = Level 3."""
        assert compute_gravity_level(None, True, None, _creds("confirmed")) == 3

    def test_domain_plus_confirmed_degree(self):
        assert compute_gravity_level("example.com", False, None, _creds("confirmed")) == 3

    def test_orcid_plus_confirmed_degree(self):
        assert compute_gravity_level(None, False, "0000-0001-2345-6789", _creds("confirmed")) == 3

    def test_one_id_plus_three_claimed(self):
        """1 identity + 3 claimed = 3 pts → Level 3."""
        assert compute_gravity_level(None, True, None, _creds("claimed", "claimed", "claimed")) == 3

    def test_one_id_plus_supported_and_claimed(self):
        """1 identity + supported (2) + claimed (1) = 3 pts → Level 3."""
        assert compute_gravity_level(None, True, None, _creds("supported", "claimed")) == 3


# ---------------------------------------------------------------------------
# Level 4: 2+ ids + 3 cred pts, OR 1 id + 6 cred pts
# ---------------------------------------------------------------------------


class TestLevel4:
    def test_two_ids_plus_confirmed(self):
        """2 identities + 1 confirmed (3 pts) → Level 4."""
        assert compute_gravity_level("example.com", True, None, _creds("confirmed")) == 4

    def test_two_ids_plus_three_claimed(self):
        """2 identities + 3 claimed (3 pts) → Level 4."""
        assert compute_gravity_level(None, True, "0000-0001-2345-6789", _creds("claimed", "claimed", "claimed")) == 4

    def test_one_id_plus_six_points(self):
        """1 identity + 6 credential points → Level 4."""
        assert compute_gravity_level(None, True, None, _creds("confirmed", "confirmed")) == 4

    def test_one_id_plus_six_claimed(self):
        """1 identity + 6 claimed (6 pts) → Level 4."""
        assert compute_gravity_level("example.com", False, None, _creds(*["claimed"] * 6)) == 4

    def test_three_ids_plus_confirmed(self):
        """3 identities + 1 confirmed (3 pts) → Level 4."""
        assert compute_gravity_level("example.com", True, "0000-0001-2345-6789", _creds("confirmed")) == 4

    def test_two_ids_plus_two_supported(self):
        """2 identities + 2 supported (4 pts, >= 3) → Level 4."""
        assert compute_gravity_level("example.com", True, None, _creds("supported", "supported")) == 4


# ---------------------------------------------------------------------------
# Level 5: 2+ ids + 6 cred pts
# ---------------------------------------------------------------------------


class TestLevel5:
    def test_two_ids_plus_two_confirmed(self):
        """2 identities + 2 confirmed (6 pts) → Level 5."""
        assert compute_gravity_level("example.com", True, None, _creds("confirmed", "confirmed")) == 5

    def test_three_ids_plus_two_confirmed(self):
        """3 identities + 2 confirmed (6 pts) → Level 5."""
        assert compute_gravity_level("example.com", True, "0000-0001-2345-6789", _creds("confirmed", "confirmed")) == 5

    def test_two_ids_plus_three_supported(self):
        """2 identities + 3 supported (6 pts) → Level 5."""
        assert compute_gravity_level(None, True, "0000-0001-2345-6789", _creds("supported", "supported", "supported")) == 5

    def test_two_ids_plus_six_claimed(self):
        """2 identities + 6 claimed (6 pts) → Level 5."""
        assert compute_gravity_level("example.com", True, None, _creds(*["claimed"] * 6)) == 5

    def test_one_id_plus_six_points_is_level_4_not_5(self):
        """1 identity + 6 pts = Level 4, NOT 5 (needs 2+ ids for Level 5)."""
        assert compute_gravity_level(None, True, None, _creds("confirmed", "confirmed")) == 4


# ---------------------------------------------------------------------------
# compute_credential_points
# ---------------------------------------------------------------------------


class TestCredentialPoints:
    def test_empty(self):
        assert compute_credential_points(None) == 0
        assert compute_credential_points([]) == 0

    def test_confirmed(self):
        assert compute_credential_points(_creds("confirmed")) == 3

    def test_supported(self):
        assert compute_credential_points(_creds("supported")) == 2

    def test_claimed(self):
        assert compute_credential_points(_creds("claimed")) == 1

    def test_mixed(self):
        assert compute_credential_points(_creds("confirmed", "supported", "claimed")) == 6

    def test_unknown_tier(self):
        assert compute_credential_points(_creds("unknown")) == 0


# ---------------------------------------------------------------------------
# get_next_level_instructions
# ---------------------------------------------------------------------------


class TestNextLevelInstructions:
    def test_level_0_suggests_identity(self):
        result = get_next_level_instructions(0)
        assert result is not None
        assert "Level 1" in result

    def test_level_0_suggests_linkedin_if_no_linkedin(self):
        result = get_next_level_instructions(0, verified_linkedin=False)
        assert result is not None

    def test_level_5_returns_none(self):
        assert get_next_level_instructions(5) is None

    def test_level_1_with_linkedin_suggests_more(self):
        result = get_next_level_instructions(1, verified_linkedin=True)
        assert result is not None
        assert "Level 2" in result

    def test_level_3_suggests_credentials(self):
        result = get_next_level_instructions(
            3, verified_linkedin=True, credential_points=0
        )
        assert result is not None
        assert "Level 4" in result
        assert "credential" in result.lower()

    def test_level_4_suggests_more_credentials(self):
        result = get_next_level_instructions(
            4, verified_linkedin=True, orcid_id="0000-0001-2345-6789", credential_points=3
        )
        assert result is not None
        assert "Level 5" in result


# ---------------------------------------------------------------------------
# GRAVITY_MULTIPLIERS consistency
# ---------------------------------------------------------------------------


class TestMultipliers:
    def test_all_levels_have_multipliers(self):
        for level in range(6):
            assert level in GRAVITY_MULTIPLIERS

    def test_multipliers_increase(self):
        for level in range(5):
            assert GRAVITY_MULTIPLIERS[level] < GRAVITY_MULTIPLIERS[level + 1]
