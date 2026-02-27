"""Test publish endpoint — requires database (integration tests)."""

import pytest

# These tests require a running database to work.
# They are structured to run against the async test client.
# For unit tests without DB, see test_quality.py.

LONG_CONTENT = "# Introduction\n\n" + " ".join(["word"] * 350)


@pytest.mark.asyncio
async def test_publish_missing_content(client):
    """Publish with empty content should fail."""
    resp = await client.post("/v1/publish", json={
        "title": "Test",
        "content": "",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_missing_title(client):
    """Publish with missing title should fail."""
    resp = await client.post("/v1/publish", json={
        "content": LONG_CONTENT,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_too_short(client):
    """Publish with <300 words should fail."""
    resp = await client.post("/v1/publish", json={
        "title": "Short",
        "content": "# Hello\n\nToo short.",
    })
    # Should be 422 (too few words)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_no_heading(client):
    """Publish without any heading should fail."""
    content = " ".join(["word"] * 350)
    resp = await client.post("/v1/publish", json={
        "title": "No Heading Doc",
        "content": content,
    })
    assert resp.status_code == 422
