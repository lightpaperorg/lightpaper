"""Markdown rendering: markdown-it-py + Pygments code highlighting."""

import hashlib
import re

from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer


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


def render_markdown(content: str) -> str:
    """Render markdown content to HTML."""
    return md.render(content)


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
