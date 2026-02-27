"""Test search API — requires database (integration tests)."""

import pytest


@pytest.mark.asyncio
async def test_search_no_query(client):
    """Search with no query should return results (all listed docs)."""
    resp = await client.get("/v1/search")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_search_with_query(client):
    """Search with a query string."""
    resp = await client.get("/v1/search", params={"q": "test"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_search_pagination(client):
    """Search supports limit and offset."""
    resp = await client.get("/v1/search", params={"limit": 5, "offset": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["limit"] == 5
    assert data["offset"] == 0
