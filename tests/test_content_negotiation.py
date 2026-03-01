"""Test content negotiation — same URL returns HTML vs JSON."""

import pytest

# Tests that don't need a database


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health endpoint always returns JSON."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_landing_page_returns_html(client):
    """GET / should return HTML."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "lightpaper.org" in resp.text


@pytest.mark.asyncio
async def test_robots_txt(client):
    """GET /robots.txt should return plain text."""
    resp = await client.get("/robots.txt")
    assert resp.status_code == 200
    assert "User-agent" in resp.text


@pytest.mark.asyncio
async def test_llms_txt(client):
    """GET /llms.txt should return plain text."""
    resp = await client.get("/llms.txt")
    assert resp.status_code == 200
    assert "lightpaper.org" in resp.text
    assert "/v1/publish" in resp.text


# Tests below require database — mark with db marker


@pytest.mark.asyncio
@pytest.mark.db
async def test_sitemap_xml(client):
    """GET /sitemap.xml should return XML."""
    resp = await client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "urlset" in resp.text


@pytest.mark.asyncio
@pytest.mark.db
async def test_slug_not_found(client):
    """GET /{nonexistent-slug} should return 404."""
    resp = await client.get("/this-slug-does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
@pytest.mark.db
async def test_doc_id_not_found(client):
    """GET /d/{nonexistent-id} should return 404."""
    resp = await client.get("/d/doc_nonexistent")
    assert resp.status_code == 404
