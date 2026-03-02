"""Test publish endpoint validation — overrides auth since account is required."""

import pytest

from app.auth import AuthResult, require_account
from app.main import app

LONG_CONTENT = "# Introduction\n\n" + " ".join(["word"] * 350)

# Mock auth that returns a fake authenticated account
_fake_account = type("Account", (), {
    "id": "00000000-0000-0000-0000-000000000000",
    "gravity_level": 0,
    "verified_domain": None,
    "verified_linkedin": None,
    "orcid_id": None,
})()

_fake_auth = AuthResult(account=_fake_account, gravity_level=0)


async def _override_require_account():
    return _fake_auth


# Override auth dependency for all publish tests
app.dependency_overrides[require_account] = _override_require_account


@pytest.mark.asyncio
async def test_publish_missing_content(client):
    """Publish with empty content should fail."""
    resp = await client.post(
        "/v1/publish",
        json={
            "title": "Test",
            "content": "",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_missing_title(client):
    """Publish with missing title should fail."""
    resp = await client.post(
        "/v1/publish",
        json={
            "content": LONG_CONTENT,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_too_short(client):
    """Publish with <300 words should fail."""
    resp = await client.post(
        "/v1/publish",
        json={
            "title": "Short",
            "content": "# Hello\n\nToo short.",
        },
    )
    # Should be 422 (too few words)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_no_heading(client):
    """Publish without any heading should fail."""
    content = " ".join(["word"] * 350)
    resp = await client.post(
        "/v1/publish",
        json={
            "title": "No Heading Doc",
            "content": content,
        },
    )
    assert resp.status_code == 422
