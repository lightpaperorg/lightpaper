"""Tests for XSS sanitization in the markdown renderer."""

from app.services.renderer import render_markdown


def test_script_tag_stripped():
    """Script tags in markdown must be stripped by nh3."""
    html = render_markdown("# Hello\n\n<script>alert(document.cookie)</script>")
    assert "<script>" not in html
    assert "alert(" not in html


def test_onerror_attribute_stripped():
    """Event handler attributes must be stripped."""
    html = render_markdown('# Test\n\n<img src="x" onerror="alert(1)">')
    assert "onerror" not in html


def test_javascript_href_stripped():
    """javascript: URLs in links must be stripped."""
    html = render_markdown('# Test\n\n<a href="javascript:alert(1)">click</a>')
    assert "javascript:" not in html


def test_iframe_stripped():
    """Iframe tags must be stripped."""
    html = render_markdown("# Test\n\n<iframe src='https://evil.com'></iframe>")
    assert "<iframe" not in html


def test_svg_onload_stripped():
    """SVG with onload must be stripped."""
    html = render_markdown('# Test\n\n<svg onload="alert(1)"></svg>')
    assert "onload" not in html
    assert "<svg" not in html


def test_style_tag_stripped():
    """Style tags with expressions must be stripped."""
    html = render_markdown("# Test\n\n<style>body { background: url('javascript:alert(1)') }</style>")
    assert "<style>" not in html


def test_safe_html_preserved():
    """Safe markdown elements should render correctly."""
    html = render_markdown("# Heading\n\n**bold** and *italic*\n\n- list item\n\n```python\nprint('hi')\n```")
    assert "<h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<li>" in html


def test_link_gets_rel_noopener():
    """Links should get rel=noopener noreferrer."""
    html = render_markdown('# Test\n\n[click](https://example.com)')
    assert "noopener" in html


def test_table_preserved():
    """Markdown tables should render."""
    md = "# Test\n\n| A | B |\n|---|---|\n| 1 | 2 |"
    html = render_markdown(md)
    assert "<table>" in html
    assert "<td>" in html


def test_nested_script_in_attribute():
    """Script injection via attribute values must be blocked."""
    html = render_markdown('# Test\n\n<div style="background:url(javascript:alert(1))">text</div>')
    assert "javascript:" not in html
