"""Shared API key generation utility."""

import secrets

import bcrypt


def generate_api_key(tier: str = "free") -> tuple[str, str, str]:
    """Generate an API key and return (full_key, key_hash, key_prefix)."""
    prefix_map = {"free": "lp_free_", "pro": "lp_live_", "test": "lp_test_"}
    prefix = prefix_map.get(tier, "lp_free_")
    token = secrets.token_urlsafe(24)
    full_key = f"{prefix}{token}"
    key_hash = bcrypt.hashpw(full_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    key_prefix = full_key[:8]
    return full_key, key_hash, key_prefix
