"""Print-ready interior PDF generation using WeasyPrint + CSS Paged Media.

Generates 6"×9" trade paperback PDFs with proper margins, front matter,
chapter breaks on recto pages, running headers, and page numbers.
"""

from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime
from io import BytesIO

from app.services.licenses import get_license_info


# --- Constants ---

TRIM_W_IN = 6.0
TRIM_H_IN = 9.0

# Margins
GUTTER_IN = 0.75   # inside margin (binding side)
OUTER_IN = 0.5     # outside margin
TOP_IN = 0.75
BOTTOM_IN = 0.625


def _build_interior_html(
    book_title: str,
    subtitle: str | None,
    authors: list[dict],
    chapters: list[dict],
    license_key: str,
    content_hash: str,
    pub_date: datetime | None,
    isbn: str | None = None,
) -> str:
    """Build full HTML document for WeasyPrint interior rendering.

    Each chapter dict has: title, rendered_html, chapter_number.
    """
    author_names = ", ".join(a.get("name", "") for a in authors) if authors else ""
    license_info = get_license_info(license_key)
    pub_year = pub_date.year if pub_date else datetime.now().year
    copyright_line = f"\u00a9 {pub_year} {author_names}" if author_names else f"\u00a9 {pub_year}"

    isbn_line = f"<p>ISBN: {isbn}</p>" if isbn else '<p class="isbn-placeholder">ISBN: [pending]</p>'

    # Build chapter HTML
    chapter_sections = []
    toc_entries = []
    for ch in chapters:
        ch_num = ch["chapter_number"]
        ch_title = ch["title"]
        toc_entries.append(f'<li><span class="toc-num">Chapter {ch_num}.</span> {ch_title}</li>')
        chapter_sections.append(
            f'<section class="chapter" id="ch{ch_num}">'
            f'<h1 class="chapter-title">{ch_title}</h1>'
            f'{ch["rendered_html"]}'
            f'</section>'
        )

    toc_html = "\n".join(toc_entries)
    chapters_html = "\n".join(chapter_sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
/* ================================================================
   PAGE SETUP — 6"×9" trade paperback
   ================================================================ */
@page {{
    size: {TRIM_W_IN}in {TRIM_H_IN}in;
    margin-top: {TOP_IN}in;
    margin-bottom: {BOTTOM_IN}in;

    @bottom-center {{
        content: counter(page);
        font-family: 'Liberation Serif', Georgia, serif;
        font-size: 10pt;
        color: #555;
    }}
}}

/* Recto (right/odd) pages: gutter on left */
@page :right {{
    margin-left: {GUTTER_IN}in;
    margin-right: {OUTER_IN}in;
    @top-right {{
        content: string(chapter-title);
        font-family: 'Liberation Serif', Georgia, serif;
        font-size: 8pt;
        font-style: italic;
        color: #888;
    }}
}}

/* Verso (left/even) pages: gutter on right */
@page :left {{
    margin-left: {OUTER_IN}in;
    margin-right: {GUTTER_IN}in;
    @top-left {{
        content: "{book_title}";
        font-family: 'Liberation Serif', Georgia, serif;
        font-size: 8pt;
        font-style: italic;
        color: #888;
    }}
}}

/* Front matter pages: roman numerals, no running headers */
@page front {{
    @bottom-center {{
        content: counter(page, lower-roman);
        font-family: 'Liberation Serif', Georgia, serif;
        font-size: 10pt;
        color: #555;
    }}
    @top-left {{ content: none; }}
    @top-right {{ content: none; }}
}}

/* Blank pages (inserted for recto start): no content at all */
@page blank {{
    @bottom-center {{ content: none; }}
    @top-left {{ content: none; }}
    @top-right {{ content: none; }}
}}

/* Chapter opening page: no running header, page number only */
@page chapter-first {{
    @top-left {{ content: none; }}
    @top-right {{ content: none; }}
}}

/* ================================================================
   BASE TYPOGRAPHY
   ================================================================ */
body {{
    font-family: 'Liberation Serif', Georgia, serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #1a1a1a;
    widows: 3;
    orphans: 3;
}}

/* ================================================================
   FRONT MATTER
   ================================================================ */
.front-matter {{
    page: front;
    counter-reset: page 1;
}}

/* Half-title */
.half-title {{
    page-break-after: always;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
}}
.half-title h1 {{
    font-size: 22pt;
    font-weight: 400;
    letter-spacing: 0.02em;
}}

/* Blank verso after half-title */
.blank-page {{
    page: blank;
    page-break-after: always;
    height: 100%;
}}

/* Full title page */
.title-page {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
}}
.title-page h1 {{
    font-size: 28pt;
    font-weight: 700;
    margin-bottom: 8pt;
}}
.title-page .subtitle {{
    font-size: 16pt;
    font-style: italic;
    color: #555;
    margin-bottom: 24pt;
}}
.title-page .authors {{
    font-size: 14pt;
    color: #333;
}}

/* Copyright page */
.copyright-page {{
    page-break-after: always;
    font-size: 9pt;
    line-height: 1.6;
    color: #555;
    padding-top: 60%;
}}
.copyright-page p {{
    margin-bottom: 6pt;
}}
.copyright-page .hash {{
    font-family: 'Liberation Mono', monospace;
    font-size: 7pt;
    word-break: break-all;
}}

/* Table of Contents */
.toc-page {{
    page-break-after: always;
}}
.toc-page h1 {{
    font-size: 18pt;
    font-weight: 700;
    margin-bottom: 18pt;
    text-align: center;
}}
.toc-page ol {{
    list-style: none;
    padding: 0;
}}
.toc-page li {{
    padding: 4pt 0;
    font-size: 11pt;
    border-bottom: 0.5pt dotted #ccc;
}}
.toc-page .toc-num {{
    font-weight: 600;
    margin-right: 6pt;
}}

/* ================================================================
   CHAPTERS
   ================================================================ */
.chapter {{
    page: auto;
    page-break-before: right; /* always start on recto */
    counter-reset: footnote;
}}

.chapter:first-of-type {{
    counter-reset: page 1;
}}

.chapter-title {{
    string-set: chapter-title content();
    font-size: 22pt;
    font-weight: 700;
    margin-top: 2in;
    margin-bottom: 24pt;
    text-align: center;
    page: chapter-first;
}}

/* Body content */
.chapter h2 {{
    font-family: 'Inter', 'Liberation Sans', sans-serif;
    font-size: 14pt;
    font-weight: 600;
    margin-top: 24pt;
    margin-bottom: 8pt;
}}
.chapter h3 {{
    font-family: 'Inter', 'Liberation Sans', sans-serif;
    font-size: 12pt;
    font-weight: 600;
    margin-top: 18pt;
    margin-bottom: 6pt;
}}
.chapter p {{
    margin-bottom: 8pt;
    text-align: justify;
    hyphens: auto;
}}
.chapter blockquote {{
    margin: 12pt 0 12pt 24pt;
    padding-left: 12pt;
    border-left: 2pt solid #ccc;
    font-style: italic;
    color: #444;
}}
.chapter pre {{
    font-family: 'Liberation Mono', monospace;
    font-size: 8.5pt;
    line-height: 1.4;
    background: #f5f5f5;
    padding: 8pt;
    border: 0.5pt solid #ddd;
    overflow: hidden;
    margin-bottom: 10pt;
    white-space: pre-wrap;
    word-wrap: break-word;
}}
.chapter code {{
    font-family: 'Liberation Mono', monospace;
    font-size: 0.9em;
}}
.chapter :not(pre) > code {{
    background: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
}}
.chapter ul, .chapter ol {{
    margin-bottom: 10pt;
    padding-left: 24pt;
}}
.chapter li {{
    margin-bottom: 3pt;
}}
.chapter table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12pt;
    font-size: 10pt;
}}
.chapter th, .chapter td {{
    border: 0.5pt solid #999;
    padding: 4pt 6pt;
    text-align: left;
}}
.chapter th {{
    background: #f0f0f0;
    font-weight: 600;
}}
.chapter img {{
    max-width: 100%;
    height: auto;
}}

/* Footnotes in print */
.chapter .footnotes {{
    font-size: 9pt;
    border-top: 0.5pt solid #ccc;
    margin-top: 24pt;
    padding-top: 8pt;
}}
</style>
</head>
<body>

<!-- FRONT MATTER -->
<div class="front-matter">
    <div class="half-title"><h1>{book_title}</h1></div>
    <div class="blank-page">&nbsp;</div>
    <div class="title-page">
        <h1>{book_title}</h1>
        {"<p class='subtitle'>" + (subtitle or "") + "</p>" if subtitle else ""}
        <p class="authors">{author_names}</p>
    </div>
    <div class="copyright-page">
        <p>{copyright_line}. {license_info['short']}.</p>
        {"<p>License: " + license_info['name'] + "</p>" if license_info['url'] else ""}
        {isbn_line}
        <p class="hash">Content hash: {content_hash}</p>
        <p>Published on lightpaper.org</p>
    </div>
    <div class="toc-page">
        <h1>Contents</h1>
        <ol>{toc_html}</ol>
    </div>
</div>

<!-- CHAPTERS -->
{chapters_html}

</body>
</html>"""


def _compute_book_hash(chapters: list[dict]) -> str:
    """SHA-256 of concatenated chapter content."""
    h = hashlib.sha256()
    for ch in chapters:
        h.update(ch.get("content", "").encode("utf-8"))
    return f"sha256:{h.hexdigest()}"


async def generate_interior_pdf(
    book_title: str,
    subtitle: str | None,
    authors: list[dict],
    chapters: list[dict],
    license_key: str,
    pub_date: datetime | None,
    isbn: str | None = None,
) -> bytes:
    """Generate full interior PDF. CPU-bound — runs in thread."""
    content_hash = _compute_book_hash(chapters)
    html = _build_interior_html(
        book_title=book_title,
        subtitle=subtitle,
        authors=authors,
        chapters=chapters,
        license_key=license_key,
        content_hash=content_hash,
        pub_date=pub_date,
        isbn=isbn,
    )

    def _render():
        from weasyprint import HTML
        return HTML(string=html).write_pdf()

    return await asyncio.to_thread(_render)


async def generate_preview_pdf(full_pdf: bytes, max_pages: int = 10) -> bytes:
    """Extract first N pages from a full interior PDF using pikepdf."""
    def _extract():
        import pikepdf
        src = pikepdf.open(BytesIO(full_pdf))
        dst = pikepdf.new()
        pages_to_copy = min(max_pages, len(src.pages))
        for i in range(pages_to_copy):
            dst.pages.append(src.pages[i])
        buf = BytesIO()
        dst.save(buf)
        return buf.getvalue()

    return await asyncio.to_thread(_extract)


async def generate_certificate_pdf(
    book_title: str,
    authors: list[dict],
    pub_date: datetime | None,
    content_hash: str,
    license_key: str,
    permanent_url: str,
) -> bytes:
    """Generate a single-page A4 Certificate of Publication."""
    license_info = get_license_info(license_key)
    author_names = ", ".join(a.get("name", "") for a in authors) if authors else "Unknown"
    pub_date_str = pub_date.strftime("%B %d, %Y") if pub_date else "Unknown"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
@page {{ size: A4; margin: 2cm 2.5cm; }}
body {{
    font-family: 'Liberation Serif', Georgia, serif;
    color: #1a1a1a;
    line-height: 1.6;
}}
.certificate {{
    text-align: center;
    padding-top: 3cm;
}}
h1 {{
    font-size: 28pt;
    font-weight: 400;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 2pt solid #1a1a1a;
    display: inline-block;
    padding-bottom: 8pt;
    margin-bottom: 2cm;
}}
.field {{
    margin: 0.6cm 0;
    font-size: 13pt;
}}
.field .label {{
    font-size: 10pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #666;
    display: block;
    margin-bottom: 4pt;
}}
.field .value {{
    font-size: 15pt;
    font-weight: 600;
}}
.hash {{
    font-family: 'Liberation Mono', monospace;
    font-size: 9pt;
    word-break: break-all;
    background: #f5f5f5;
    padding: 8pt 12pt;
    border-radius: 4pt;
    display: inline-block;
    margin-top: 4pt;
    max-width: 90%;
}}
.verified {{
    margin-top: 2cm;
    font-size: 11pt;
    color: #666;
    border-top: 1pt solid #ccc;
    padding-top: 1cm;
}}
</style>
</head>
<body>
<div class="certificate">
    <h1>Certificate of Publication</h1>

    <div class="field">
        <span class="label">Title</span>
        <span class="value">{book_title}</span>
    </div>

    <div class="field">
        <span class="label">Author</span>
        <span class="value">{author_names}</span>
    </div>

    <div class="field">
        <span class="label">Publication Date</span>
        <span class="value">{pub_date_str}</span>
    </div>

    <div class="field">
        <span class="label">Content Hash (SHA-256)</span>
        <div class="hash">{content_hash}</div>
    </div>

    <div class="field">
        <span class="label">License</span>
        <span class="value">{license_info['name']}</span>
    </div>

    <div class="field">
        <span class="label">Permanent URL</span>
        <span class="value">{permanent_url}</span>
    </div>

    <div class="verified">
        Verified by lightpaper.org
    </div>
</div>
</body>
</html>"""

    def _render():
        from weasyprint import HTML
        return HTML(string=html).write_pdf()

    return await asyncio.to_thread(_render)
