"""Markdown rendering: markdown-it-py + Pygments code highlighting + nh3 sanitization."""

import hashlib
import re

import nh3
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name, guess_lexer

# Allowed HTML tags after markdown rendering (nh3 sanitizer)
ALLOWED_TAGS = {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "br",
    "hr",
    "ul",
    "ol",
    "li",
    "a",
    "em",
    "strong",
    "code",
    "pre",
    "blockquote",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "img",
    "figure",
    "figcaption",
    "div",
    "span",
    "sup",
    "sub",
    "input",
    "section",
    "details",
    "summary",
    "dl",
    "dt",
    "dd",
    "del",
    "ins",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "id", "class"},  # links + footnote refs (rel set by link_rel param)
    "img": {"src", "alt", "title", "width", "height"},
    "input": {"type", "checked", "disabled"},  # task lists
    "td": {"align"},
    "th": {"align"},
    "code": {"class"},  # language class for syntax highlighting
    "pre": {"class"},
    "div": {"class", "style"},  # Pygments highlight blocks
    "span": {"class", "style"},  # Pygments inline styles
    "sup": {"class", "id"},  # footnotes
    "li": {"id"},  # footnote items
    "section": {"class"},  # footnote section
}


def _highlight_code(code: str, lang: str, _attrs: str) -> str:
    """Pygments code highlighting for fenced code blocks."""
    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = guess_lexer(code)
    except Exception:
        lexer = TextLexer(stripall=True)

    formatter = HtmlFormatter(
        cssclass="highlight",
        noclasses=True,
        style="default",
    )
    return highlight(code, lexer, formatter)


# Configure markdown-it with GFM-like features
md = MarkdownIt("gfm-like", {"highlight": _highlight_code})
footnote_plugin(md)
tasklists_plugin(md)


_STYLE_JS_RE = re.compile(r"javascript\s*:", re.IGNORECASE)


def render_markdown(content: str) -> str:
    """Render markdown content to HTML, sanitized against XSS."""
    raw_html = md.render(content)
    cleaned = nh3.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
    )
    # Strip javascript: from style attributes (nh3 doesn't sanitize CSS values)
    cleaned = _STYLE_JS_RE.sub("", cleaned)
    # Wrap tables in scroll container for mobile
    cleaned = cleaned.replace("<table>", '<div class="table-wrapper"><table>')
    cleaned = cleaned.replace("</table>", "</table></div>")
    return cleaned


def compute_content_hash(content: str) -> str:
    """SHA-256 hash of raw content."""
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"sha256:{h}"


def compute_word_count(content: str) -> int:
    """Word count excluding markdown syntax."""
    # Strip code blocks
    text = re.sub(r"```[\s\S]*?```", "", content)
    # Strip inline code
    text = re.sub(r"`[^`]+`", "", text)
    # Strip markdown links, keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Strip heading markers
    text = re.sub(r"^#{1,6}\s", "", text, flags=re.MULTILINE)
    # Strip images
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    return len(text.split())


def compute_reading_time(word_count: int) -> int:
    """Reading time in minutes (238 wpm average)."""
    return max(1, round(word_count / 238))


def extract_toc(content: str) -> list[dict]:
    """Extract table of contents from headings."""
    toc = []
    for match in re.finditer(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        # Generate anchor ID
        anchor = re.sub(r"[^\w\s-]", "", text.lower())
        anchor = re.sub(r"[\s]+", "-", anchor)
        toc.append({"level": level, "text": text, "anchor": anchor})
    return toc
