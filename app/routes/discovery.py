"""Discovery routes: robots.txt, sitemap.xml, llms.txt, OG images, IndexNow."""

import logging
from xml.sax.saxutils import escape as xml_escape

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_account
from app.config import settings
from app.database import get_db
from app.models import Account, Book, Credential, Document, DocumentVersion
from app.rate_limit import limiter
from app.services.gravity import get_gravity_badges
from app.services.og_image import generate_book_og_image, generate_og_image

logger = logging.getLogger(__name__)

router = APIRouter(tags=["discovery"])

INDEXNOW_KEY = "d3e5606fbb3758957821a552a4e8f85c"


async def notify_search_engines(urls: list[str]):
    """Notify search engines of new/updated URLs.

    - IndexNow: Bing, Yandex, DuckDuckGo, Seznam (instant)
    - Google: sitemap ping (triggers re-crawl of sitemap.xml)
    """
    if not urls or "localhost" in settings.base_url:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # IndexNow — covers Bing, Yandex, DuckDuckGo, Seznam
            payload = {
                "host": "lightpaper.org",
                "key": INDEXNOW_KEY,
                "keyLocation": f"{settings.base_url}/{INDEXNOW_KEY}.txt",
                "urlList": urls[:10000],
            }
            await client.post("https://api.indexnow.org/indexnow", json=payload)

            # Google sitemap ping — triggers Google to re-crawl sitemap.xml
            sitemap_url = f"{settings.base_url}/sitemap.xml"
            await client.get(
                "https://www.google.com/ping",
                params={"sitemap": sitemap_url},
            )
    except Exception:
        logger.warning("Search engine notification failed", exc_info=True)


# Keep old name as alias for existing imports
notify_indexnow = notify_search_engines


@router.get(f"/{INDEXNOW_KEY}.txt", response_class=PlainTextResponse, include_in_schema=False)
async def indexnow_key_file():
    """IndexNow key verification file."""
    return INDEXNOW_KEY


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return f"""User-agent: *
Allow: /
Disallow: /v1/account
Disallow: /v1/account/

# AI crawlers — explicitly welcomed for training and answer engines
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: CCBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Bytespider
Allow: /

User-agent: cohere-ai
Allow: /

Sitemap: {settings.base_url}/sitemap.xml

# AI agent instructions
# See https://llmstxt.org for the llms.txt standard
LLMs-txt: {settings.base_url}/llms.txt

# Agent discovery
# Google A2A: https://google.github.io/A2A/
# OpenAI plugin: https://platform.openai.com/docs/plugins
Agent-Json: {settings.base_url}/.well-known/agent.json
AI-Plugin: {settings.base_url}/.well-known/ai-plugin.json
"""


@router.get("/feed.xml")
async def atom_feed(db: AsyncSession = Depends(get_db)):
    """Atom feed of recent published documents and books."""
    result = await db.execute(
        select(Document)
        .where(
            Document.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.quality_score >= 40,
            Document.book_id.is_(None),  # Exclude chapters
        )
        .order_by(Document.created_at.desc())
        .limit(50)
    )
    docs = result.scalars().all()

    # Also include books
    book_result = await db.execute(
        select(Book)
        .where(
            Book.deleted_at.is_(None),
            Book.listed.is_(True),
        )
        .order_by(Book.created_at.desc())
        .limit(20)
    )
    books = book_result.scalars().all()

    # Merge and sort by created_at
    all_items = [(d.created_at, d.updated_at, "doc", d) for d in docs] + [
        (b.created_at, b.updated_at, "book", b) for b in books
    ]
    all_items.sort(key=lambda x: x[0] or datetime.min, reverse=True)
    all_items = all_items[:50]

    from datetime import datetime as datetime_cls

    updated = all_items[0][1].strftime("%Y-%m-%dT%H:%M:%SZ") if all_items else "2026-01-01T00:00:00Z"

    entries = []
    for created_at, updated_at, item_type, item in all_items:
        if item_type == "doc":
            doc = item
            slug_url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"
            published = doc.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if doc.created_at else ""
            doc_updated = doc.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if doc.updated_at else published
            author_name = ""
            if doc.authors:
                author_name = doc.authors[0].get("name", "")
            subtitle_text = f"\n      <subtitle>{xml_escape(doc.subtitle)}</subtitle>" if doc.subtitle else ""
            entries.append(f"""  <entry>
    <title>{xml_escape(doc.title)}</title>{subtitle_text}
    <link href="{xml_escape(slug_url)}" rel="alternate"/>
    <id>urn:lightpaper:{doc.id}</id>
    <published>{published}</published>
    <updated>{doc_updated}</updated>
    <author><name>{xml_escape(author_name)}</name></author>
    <summary>{xml_escape(doc.subtitle or doc.title)}</summary>
  </entry>""")
        else:
            book = item
            book_url = f"{settings.base_url}/books/{book.slug}"
            published = book.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if book.created_at else ""
            book_updated = book.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if book.updated_at else published
            author_name = ""
            if book.authors:
                author_name = book.authors[0].get("name", "")
            subtitle_text = f"\n      <subtitle>{xml_escape(book.subtitle)}</subtitle>" if book.subtitle else ""
            entries.append(f"""  <entry>
    <title>{xml_escape(book.title)}</title>{subtitle_text}
    <link href="{xml_escape(book_url)}" rel="alternate"/>
    <id>urn:lightpaper:{book.id}</id>
    <published>{published}</published>
    <updated>{book_updated}</updated>
    <author><name>{xml_escape(author_name)}</name></author>
    <summary>{xml_escape(book.subtitle or book.title)}</summary>
  </entry>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>lightpaper.org</title>
  <subtitle>API-first publishing. One call, one permanent URL.</subtitle>
  <link href="{settings.base_url}/feed.xml" rel="self"/>
  <link href="{settings.base_url}/" rel="alternate"/>
  <id>urn:lightpaper:feed</id>
  <updated>{updated}</updated>
{"".join(entries)}
</feed>"""

    return Response(content=xml, media_type="application/atom+xml")


@router.get("/feed.json")
async def json_feed(db: AsyncSession = Depends(get_db)):
    """JSON Feed 1.1 of recent published documents."""
    result = await db.execute(
        select(Document)
        .where(
            Document.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.quality_score >= 40,
        )
        .order_by(Document.created_at.desc())
        .limit(50)
    )
    docs = result.scalars().all()

    items = []
    for doc in docs:
        slug_url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"
        author_name = ""
        if doc.authors:
            author_name = doc.authors[0].get("name", "")
        item = {
            "id": f"urn:lightpaper:{doc.id}",
            "url": slug_url,
            "title": doc.title,
            "date_published": doc.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if doc.created_at else None,
            "date_modified": doc.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if doc.updated_at else None,
        }
        if doc.subtitle:
            item["summary"] = doc.subtitle
        if author_name:
            item["authors"] = [{"name": author_name}]
        if doc.tags:
            item["tags"] = doc.tags
        items.append(item)

    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "lightpaper.org",
        "home_page_url": f"{settings.base_url}/",
        "feed_url": f"{settings.base_url}/feed.json",
        "description": "API-first publishing. One call, one permanent URL.",
        "items": items,
    }

    return feed


@router.get("/.well-known/ai-plugin.json")
async def ai_plugin_json():
    """OpenAI-style agent discovery manifest."""
    return {
        "schema_version": "v1",
        "name_for_human": "lightpaper.org",
        "name_for_model": "lightpaper",
        "description_for_human": "Open-source API-first publishing. One call, one permanent URL.",
        "description_for_model": (
            "lightpaper.org is a publishing platform. Use it to publish markdown documents "
            "as permanent, discoverable web pages. Read /llms.txt for complete instructions "
            "on how to create accounts, write well, and publish."
        ),
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": f"{settings.base_url}/v1/openapi.json",
        },
        "logo_url": f"{settings.base_url}/static/apple-touch-icon.png",
        "contact_email": "hello@lightpaper.org",
        "legal_info_url": f"{settings.base_url}/privacy",
    }


@router.get("/.well-known/agent.json")
async def a2a_agent_json():
    """Google A2A protocol agent card."""
    return {
        "name": "lightpaper",
        "description": "API-first publishing platform. Publish markdown documents as permanent, discoverable web pages with quality scoring and author gravity.",
        "url": settings.base_url,
        "provider": {
            "organization": "lightpaper.org",
            "url": settings.base_url,
        },
        "version": "0.1.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "skills": [
            {
                "id": "publish",
                "name": "Publish Document",
                "description": "Publish a markdown document as a permanent, discoverable web page with quality scoring.",
                "tags": ["publishing", "markdown", "writing"],
                "examples": ["Publish an article about AI safety", "Write and publish a technical tutorial"],
            },
            {
                "id": "search",
                "name": "Search Documents",
                "description": "Full-text search across published documents with gravity-boosted ranking.",
                "tags": ["search", "discovery", "reading"],
                "examples": ["Find articles about machine learning", "Browse recent publications"],
            },
            {
                "id": "manage",
                "name": "Manage Documents",
                "description": "Update, delete, and list published documents. Track version history.",
                "tags": ["management", "editing", "versioning"],
                "examples": ["Update my article", "List my publications"],
            },
            {
                "id": "verify",
                "name": "Verify Identity",
                "description": "Verify author identity via LinkedIn, domain DNS, ORCID, and credentials for gravity boost.",
                "tags": ["verification", "identity", "trust"],
                "examples": ["Verify my LinkedIn profile", "Submit my degree for verification"],
            },
        ],
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "authentication": {
            "schemes": ["bearer"],
            "description": "API key via Authorization: Bearer header. Get one via POST /v1/auth/email + /v1/auth/verify.",
        },
        "endpoints": {
            "openapi": f"{settings.base_url}/v1/openapi.json",
            "llms_txt": f"{settings.base_url}/llms.txt",
            "mcp": f"{settings.base_url}/mcp",
        },
    }


@router.get("/.well-known/mcp-registry-auth")
async def mcp_registry_auth():
    """Public key for MCP Registry HTTP authentication."""
    return PlainTextResponse(
        "v=MCPv1; k=ed25519; p=MaCWYnZnrdcpVtHLRhyp+Tna+nuc6tDy5I+ju4LYPCQ=",
        media_type="text/plain",
    )


@router.get("/.well-known/mcp/server-card.json")
async def mcp_server_card():
    """MCP server card for Smithery and other MCP registries."""
    return {
        "name": "lightpaper",
        "description": (
            "API-first publishing platform. Publish markdown documents as permanent, "
            "discoverable web pages with quality scoring and author gravity."
        ),
        "homepage": settings.base_url,
        "icon": f"{settings.base_url}/static/apple-touch-icon.png",
        "serverUrl": f"{settings.base_url}/mcp",
        "configSchema": {
            "type": "object",
            "properties": {
                "apiKey": {
                    "type": "string",
                    "title": "API Key",
                    "description": (
                        "Your lightpaper.org API key (starts with lp_free_ or lp_live_). "
                        "Optional — tools authenticate interactively via email OTP."
                    ),
                },
            },
        },
    }


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    return f"""# lightpaper.org

> API-first publishing platform. One HTTP call, one permanent URL.

lightpaper.org is a publishing platform designed for AI agents and humans.
Publish documents via a single API call and get beautiful, permanent, discoverable URLs.

## IMPORTANT: How to publish well (read this first)

If a user asks you to write and publish something, follow this flow:

### First-time onboarding (email → LinkedIn → credentials → done)

Do all of these steps in the same session. Once complete, the user has an API key and never needs to onboard again.

**Step 1: Create account via email OTP**

Ask the user for three things:
- Their name (display name)
- Their email
- Their preferred handle (like a username — used in their profile URL /@handle)

Then send a verification code:

POST {settings.base_url}/v1/auth/email
Content-Type: application/json

{{"email": "user@example.com", "display_name": "Alice Smith", "handle": "alice"}}

→ Returns: {{"session_id": "xxx", "message": "Code sent to u***@example.com", "expires_in": 600}}

Ask the user to check their email for the 6-digit code, then verify:

POST {settings.base_url}/v1/auth/verify
Content-Type: application/json

{{"session_id": "xxx", "code": "847293"}}

→ Returns: {{"api_key": "lp_free_xxx", "account_id": "...", "handle": "alice", "is_new_account": true, "gravity_level": 0, "next_level": "..."}}

SAVE THE api_key — you need it for every subsequent call.

**Step 2: Connect LinkedIn (recommended — gets gravity Level 1)**

Immediately offer LinkedIn verification. This is the easiest identity verification and most users have LinkedIn.

POST {settings.base_url}/v1/account/verify/linkedin
Authorization: Bearer <api_key>

→ Returns: {{"authorization_url": "https://linkedin.com/oauth/...", "state": "xxx"}}

Tell the user to open the URL in their browser. Poll every 3-5 seconds until complete (timeout after 5 minutes):

GET {settings.base_url}/v1/account/verify/linkedin/check
Authorization: Bearer <api_key>

→ Returns: {{"verified": true, "gravity_level": 1}}

Note: LinkedIn login (POST /v1/auth/linkedin) and LinkedIn verification (POST /v1/account/verify/linkedin) both set verified_linkedin=True. If the user signed in via LinkedIn auth, they already have this verification.

**Step 3: Submit credentials (recommended — can reach Level 3 with just LinkedIn)**

Ask the user about their qualifications (degrees, certifications, employment) and investigate them. With LinkedIn verified + a confirmed degree (3 credential points), the user reaches gravity Level 3 (1.4x search boost) — no domain or ORCID needed.

POST {settings.base_url}/v1/account/credentials
Authorization: Bearer <api_key>
Content-Type: application/json

{{"credentials": [{{"credential_type": "degree", "institution": "University of Melbourne", "title": "Bachelor of Science", "year": 2019, "evidence_tier": "confirmed", "evidence_data": {{"api_response": {{"found": true}}}}, "agent_notes": "Verified via graduation API"}}]}}

**Step 4 (optional): Additional identity verifications**

- Domain verification: POST /v1/account/verify/domain (DNS TXT record)
- ORCID verification: POST /v1/account/verify/orcid (fully automatable, no browser)

Each additional identity verification increases gravity level.

### Returning users

If the user already has an API key, skip onboarding. Just use it in the Authorization header.
If the user says they have a key but you don't have it in your environment, ask them for it.

If the user needs to sign in again, use the same email OTP flow — it works for login too. Check the `is_new_account` field in the auth_verify response:
- **true** → new account, proceed with LinkedIn/credentials/verification steps above
- **false** → returning user, check GET /v1/account/gravity to see current level before offering further verifications

If the user signed in via LinkedIn OAuth (POST /v1/auth/linkedin), they already have LinkedIn verified.

### Publishing existing content

If the user already has written content (a markdown file, draft, or pasted text):
1. Read the file or accept the pasted content
2. Ensure it has 300+ words and at least one heading — add headings if missing
3. Add a title and subtitle if not already present
4. Publish with the appropriate format

### Writing the article

Write real, substantive markdown content. To score well (60+ quality), include:
- A compelling title AND subtitle (subtitle shows in sharing previews on WhatsApp, Slack, LinkedIn, etc.)
- At least 500 words (300 minimum, but 500+ scores much better)
- Multiple headings (## Section Name) to structure the content
- At least one list, code block, or table for variety
- 2+ external links to sources, and ideally a ## References section at the end
- Professional tone — no clickbait, no ALL CAPS, no excessive exclamation marks

### Pick the right format

- **"post"** (default) — Clean sans-serif blog style. Use for tutorials, how-to guides, technical writeups, announcements, general articles.
- **"paper"** — Serif font (Palatino), numbered headings (1., 1.1), first blockquote becomes labeled "Abstract" box. Use for research papers, literature reviews, technical analyses. Start content with `> Your abstract text here...`
- **"essay"** — Elegant serif (Georgia), drop cap on first paragraph, pull-quote blockquotes, ornamental dividers. Use for sustained arguments, cultural commentary, personal narratives, opinion pieces.

How to choose: citations + methodology + findings → `paper`. Sustained argument or narrative → `essay`. Practical, instructional, or code-heavy → `post`.

### Format-specific writing tips

**Paper format** — start with a blockquote abstract, use ## headings for sections (they auto-number), include a ## References section:
```
> This paper examines the effects of X on Y. We find that...

## Introduction

The problem of X has been studied extensively [^1]...

## References

[^1]: Smith, J. (2024). Title. *Journal*, 12(3), 45-67.
```

**Essay format** — start directly with a paragraph (gets a drop cap), use ## headings as section markers, use > for pull-quotes:
```
The thing about revolutions is that nobody sees them coming...

## The Quiet Shift

> We were so busy watching the front door that we missed the window.
```

**Footnote syntax** — use `[^1]` in text and `[^1]: Citation text` at the bottom. Footnotes earn up to 7 quality points (3+ footnotes = 7 pts).

### Publish with all fields

POST {settings.base_url}/v1/publish
Authorization: Bearer <api_key>
Content-Type: application/json

{{"title": "Why Pigs Can't Fly", "subtitle": "The biomechanics, evolution, and physics behind grounded swine", "content": "# Why Pigs Can't Fly\\n\\nMarkdown content here with 500+ words...", "format": "post", "authors": [{{"name": "Alice Smith", "handle": "alice"}}], "tags": ["biology", "physics"]}}

→ Returns: {{"url": "https://lightpaper.org/why-pigs-cant-fly", "permanent_url": "https://lightpaper.org/d/doc_xxx", "quality_score": 72, "quality_suggestions": [...]}}

### Share the result

Always tell the user:
- The URL of their published article
- The quality score and any suggestions for improvement
- If quality < 60, offer to revise and update it (PUT /v1/documents/{{id}})

### Update an existing article

To update, you need the document ID. List the user's documents first:
GET {settings.base_url}/v1/account/documents (requires auth) → returns all documents with IDs, format, tags, and quality scores.
Then: PUT /v1/documents/{{id}} with the fields to update (title, subtitle, content, format, authors, tags, listed).
Content changes create a new version (max 100). Quality score is recalculated on content change.
Format can be changed at any time (e.g., switching from "post" to "paper").

### Improving quality on existing articles

To improve an existing article's quality score:
1. GET /v1/documents/{{id}} — fetch the current content
2. Review against quality criteria: structure (headings, paragraphs), substance (word count, code/lists/tables), tone (no clickbait), attribution (links, references, footnotes)
3. Rewrite to address gaps
4. PUT /v1/documents/{{id}} with the improved content — quality score is recalculated

### Browsing and discovering articles

GET /v1/search supports browsing without a search query:
- `?sort=recent&limit=10` — latest published articles
- `?sort=quality&limit=10` — highest-rated articles
- `?author=alice` — articles by a specific author
- `?tags=python,ml` — articles with specific tags
All filters can be combined.

### Account is required

Anonymous publishing is not supported. All publishing, updating, and verification endpoints require authentication. If the user doesn't have an account, walk them through the email signup flow (Step 1 above) — it takes 30 seconds.

## API Reference

Base URL: {settings.base_url}
All endpoints return JSON. Authorization via `Authorization: Bearer <api_key>` header.

### Account & Authentication
- POST /v1/auth/email — Send a 6-digit verification code to an email (signup or login). 5/hour.
- POST /v1/auth/verify — Verify the code → returns account + API key. 10/hour.
- POST /v1/auth/linkedin — Start LinkedIn OAuth for login/signup → returns authorization_url. 10/hour.
- GET /v1/auth/linkedin/callback — LinkedIn OAuth callback (browser, not called by agents).
- GET /v1/auth/linkedin/poll?session_id=xxx — Poll for LinkedIn OAuth completion → returns API key. Poll every 3-5 seconds.
- GET /v1/account — Get account info (handle, gravity level, verification status, badges)
- DELETE /v1/account — Hard-delete account and all data (GDPR)
- POST /v1/account/keys — Generate additional API keys
- GET /v1/account/keys — List API keys (prefixes only)
- DELETE /v1/account/keys/{{prefix}} — Revoke an API key

### Publishing & Documents
- POST /v1/publish — Publish a document (see Publishing section below). 60/hour.
- GET /v1/documents/{{id}} — Get document by ID (public, no auth needed)
- PUT /v1/documents/{{id}} — Update a document (owner only, creates new version)
- DELETE /v1/documents/{{id}} — Soft-delete a document (owner only, returns 204)
- GET /v1/documents/{{id}}/versions — List version history

### Search
- GET /v1/search?q=query — Full-text search with ranking. 60/minute.
  - `q` (optional) — Full-text query. Omit to browse all listed articles.
  - `author` — Filter by author handle (e.g. `?author=alice`)
  - `tags` — Comma-separated tag filter (e.g. `?tags=python,ml`)
  - `min_quality` — Minimum quality score 0-100 (default 40)
  - `sort` — `relevance` (default), `recent`, or `quality`
  - `limit` — Results per page, 1-100 (default 20)
  - `offset` — Pagination offset (default 0)

### Reading & Content Negotiation
All reading routes support content negotiation via Accept header:
- `Accept: text/html` → rendered HTML page (default)
- `Accept: application/json` → structured JSON

Routes:
- GET /{{slug}} — Read document by URL slug
- GET /d/{{id}} — Read document by permanent ID
- GET /@{{handle}} — View author profile with published documents

### Author Profiles
- GET /@{{handle}} — Public author profile page
  - HTML: Displays name, handle, bio, gravity badges, and published document list
  - JSON: Returns {{"handle", "display_name", "bio", "gravity_level", "gravity_badges", "member_since", "documents": [...]}}
  - Each document includes: id, title, url, quality_score, reading_time, created_at

### Verification & Gravity
- POST /v1/account/verify/domain — Start DNS domain verification → returns TXT record to add
- GET /v1/account/verify/domain/check — Check if DNS TXT record has propagated
- POST /v1/account/verify/linkedin — Start LinkedIn OAuth → returns authorization_url for user
- GET /v1/account/verify/linkedin/check — Poll LinkedIn OAuth completion
- POST /v1/account/verify/orcid — Verify ORCID iD (fully automatable, no browser)
- POST /v1/account/credentials — Submit verified credentials (see Credential Verification below)
- GET /v1/account/credentials — List all submitted credentials
- GET /v1/account/gravity — Get gravity level, multiplier, featured threshold, next-level instructions

## Authentication

An account is required to publish. Sign in first via POST /v1/auth/email + /v1/auth/verify.

| Method | How | What you get |
|--------|-----|-------------|
| **API key** (recommended) | `Authorization: Bearer lp_free_xxx` from POST /v1/auth/email + /v1/auth/verify | Full access: author names, search visibility, profiles, verification, document management |
| **Firebase** (legacy) | `Authorization: Bearer <id_token>` | Browser-based flows, same capabilities as API key |

## Publishing

POST /v1/publish — requires markdown content with at least 300 words and at least one heading (e.g. `# Introduction`).

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Document title (max 500 chars) |
| content | string | Yes | Markdown content (min 300 words, max 500K chars, must have ≥1 heading) |
| subtitle | string | No | Subtitle (max 1000 chars) |
| format | string | No | Presentation format: "paper", "essay", "post" (default "post") |
| authors | array | No | Author attribution: [{{"name": "Alice", "handle": "alice"}}] (max 20). Co-authors don't need accounts — just include their name. |
| tags | list | No | Tags for search filtering (max 50) |
| options.slug | string | No | Custom URL slug (max 80 chars, auto-generated from title if omitted) |
| options.listed | bool | No | List in search results and sitemap (default true) |
| metadata | dict | No | Custom metadata (max 50KB serialized) |

### Response Fields

The publish response includes:
- `url` — Readable URL (e.g. https://lightpaper.org/my-document)
- `permanent_url` — Permanent URL by ID (e.g. https://lightpaper.org/d/doc_xxx)
- `quality_score` — Score 0-100 (see Quality Score section)
- `quality_breakdown` — {{structure, substance, tone, attribution}} — each 0-25
- `quality_suggestions` — List of actionable improvement tips
- `author_gravity` — Author's gravity level (0-5)
- `gravity_note` — Instructions for reaching the next gravity level

### Document Formats

Use `format` to control the visual presentation. Choose based on the content's nature — the format dramatically changes how the document looks and reads. All formats use the same markdown renderer — format only affects layout and typography.

**"paper"** — Use for research papers, literature reviews, technical analyses, methodology papers.
- Serif font (Palatino), justified text, academic density
- h2 and h3 headings are auto-numbered (1. Introduction, 1.1 Background, 2. Methods, etc.)
- First blockquote renders as a labeled "Abstract" box — write `> Your abstract text here...` at the start
- Clean academic tables (ruled top/bottom, no cell borders)
- Centered title and author block
- JSON-LD type: ScholarlyArticle
- Think: arXiv, journal articles, conference papers

**"essay"** — Use for sustained arguments, cultural commentary, personal narratives, opinion pieces, longform explorations.
- Elegant serif font (Georgia), large text (20px), generous line-height and whitespace
- Drop cap on the first paragraph
- Blockquotes styled as centered pull-quotes with decorative quotation mark
- Centered headings as section markers (not numbered)
- Ornamental section dividers (horizontal rules become decorative)
- Images extend wider than the text column for dramatic effect
- Quality and format badges are hidden — the design speaks for itself
- Think: The New Yorker, Aeon, The Atlantic longform

**"post"** (default) — Use for practical articles, tutorials, how-to guides, technical writeups, announcements.
- Clean sans-serif font (system UI), modern blog layout
- Blockquotes styled as callout boxes (background + left border accent)
- Prominent, rounded code blocks
- All metadata visible (quality score, gravity badges)
- Think: Substack, dev.to, modern technical blogs

**How to choose**: If the content has citations, methodology, and findings → `paper`. If it's a sustained argument, narrative, or cultural exploration → `essay`. If it's practical, instructional, conversational, or code-heavy → `post`.

### Document Updates

PUT /v1/documents/{{id}} — Update title, subtitle, content, format, authors, tags, listed status, or metadata.
- Content updates create a new version (max 100 versions per document). Returns 422 when limit exceeded.
- Quality score is recalculated whenever content changes.
- Only the document owner (the account that published it) can update.
- Version history is available via GET /v1/documents/{{id}}/versions.

### Document Deletion

DELETE /v1/documents/{{id}} — Soft-deletes the document (returns 204).
- The document will no longer appear in search, sitemap, or author profiles.
- The URL will return 410 Gone.
- Only the document owner can delete.

## Quality Score (0-100)

Every published document receives a deterministic quality score. This score affects search ranking and visibility.

### Components (each 0-25)

**Structure (0-25)** — Document organization
- 3+ headings: 10 pts (1-2 headings: 5 pts)
- 8+ paragraphs: 8 pts (4-7: 5 pts, 2-3: 3 pts)
- Varied paragraph lengths: up to 7 pts

**Substance (0-25)** — Content depth
- 2000+ words: 12 pts (1000+: 10, 500+: 7, 300+: 5)
- Code blocks: up to 5 pts (4+: 5, 2+: 3)
- Lists: up to 4 pts (5+ items: 4, 2+: 2)
- Tables: up to 4 pts (3+: 4, 1+: 2)

**Tone (0-25)** — Professional quality
- Starts at 18 pts (professional baseline)
- Clickbait patterns: -4 pts each (e.g. "you won't believe", "mind-blowing")
- Excessive exclamation marks (>30% of sentences): -5 pts
- Excessive ALL CAPS words (>3): -3 pts

**Attribution (0-25)** — Sources and references
- External links: up to 10 pts (5+: 10, 2+: 7, 1: 4)
- References/Bibliography section heading: 8 pts
- Footnotes [^1]: up to 7 pts (3+: 7, 1+: 4)

### Visibility Thresholds
- Documents with quality < 40 are excluded from search results and get a `noindex` meta tag.
- The featured quality threshold depends on gravity level (see Gravity section).

### How to Maximize Quality
For a score of 80+, a document should have:
- 3+ headings with varied paragraph lengths (structure ≈ 20+)
- 1000+ words with code blocks or tables (substance ≈ 15+)
- Professional tone, no clickbait (tone ≈ 18)
- 5+ external links and a References section (attribution ≈ 18+)

## Author Gravity (0-5)

Gravity is an author verification level that boosts search ranking. Higher gravity = documents rank higher. Verifications are non-hierarchical — any combination of identity verifications and credentials can reach any level.

### Identity Verifications (independent, any combination)

- **Domain**: Verify ownership of a personal/professional domain via DNS TXT record
- **LinkedIn**: Connect LinkedIn profile via OAuth (login or verification — both count)
- **ORCID**: Link an ORCID iD (fully automatable, no browser needed)

### Levels and Multipliers

| Level | Requirement | Search Multiplier | Featured Threshold |
|-------|------------|-------------------|-------------------|
| 0 | Nothing | 1.0x | Quality >= 70 |
| 1 | Any 1 identity verification | 1.1x | Quality >= 68 |
| 2 | 2 identity verifications | 1.25x | Quality >= 65 |
| 3 | 3 identities, OR 2 ids + 1 cred pt, OR 1 id + 3 cred pts | 1.4x | Quality >= 60 |
| 4 | 2+ ids + 3 cred pts, OR 1 id + 6 cred pts | 1.55x | Quality >= 57 |
| 5 | 2+ ids + 6 cred pts | 1.7x | Quality >= 55 |

Example: LinkedIn (1 identity) + confirmed degree (3 credential points) = Level 3 (1.4x boost). No domain or ORCID needed.

### Search Ranking Formula

Documents are ranked by: `text_relevance x quality_score x gravity_multiplier`

A level-3 author with quality 60 ranks equivalently to a level-0 author with quality 84.
Gravity verification is the most impactful thing an author can do for discoverability.

### How to Check Gravity

GET /v1/account/gravity returns:
```json
{{"level": 2, "multiplier": 1.25, "featured_threshold": 65, "badges": ["example.com ✓", "LinkedIn ✓"], "next_level": "To reach Level 3 (1.4x search boost): submit verified credentials (POST /v1/account/credentials)"}}
```

## Listed vs. Unlisted

- **Listed**: Document appears in search results, sitemap.xml, and author profiles (default).
- **Unlisted**: Document is readable via its URL but invisible to search and discovery.

To unlist an existing document: PUT /v1/documents/{{id}} with {{"listed": false}}
To re-list: PUT /v1/documents/{{id}} with {{"listed": true}}

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /v1/publish | 60/hour |
| GET /v1/search | 60/minute |
| GET /{{slug}}, /d/{{id}}, /@{{handle}} | 120/minute |
| POST /v1/auth/email | 5/hour (+ 3 codes/hour per email) |
| POST /v1/auth/verify | 10/hour |
| POST /v1/auth/linkedin | 10/hour |
| POST /v1/account/verify/orcid | 10/hour |
| POST /v1/account/verify/linkedin | 10/hour |
| POST /v1/account/credentials | 20/hour |
| GET /og/{{id}}.png | 30/minute |

## Credential Verification (for agents)

Agents can investigate a user's qualifications (degrees, certifications, employment) and submit
results with evidence tiers. Credentials contribute points toward gravity levels — they work
alongside any identity verification, not just domain+LinkedIn+ORCID.

### Evidence Tiers

- **confirmed** (3 points) — Institutional API or database match. Example: Curtin University graduation API returns a match.
- **supported** (2 points) — Corroborating evidence from a credible source. Examples: ORCID education record with institution-verified source, university staff page listing, My eQuals verified link.
- **claimed** (1 point) — User's word only, no independent verification.

### Credential Points + Identity → Gravity Levels

Credential points combine with identity verifications to determine gravity level:
- **1 identity + 3 cred pts** = Level 3 (e.g., LinkedIn + confirmed degree)
- **2 identities + 3 cred pts** = Level 4 (e.g., LinkedIn + ORCID + confirmed degree)
- **1 identity + 6 cred pts** = Level 4 (e.g., domain + 2 confirmed credentials)
- **2 identities + 6 cred pts** = Level 5

Note: At least 1 identity verification is required for credential points to count.

### Investigation Strategies

**If the institution has an API:**
- Query it directly (see Known Verification APIs below)
- If it returns a match → evidence_tier="confirmed" (3 pts)

**If no API exists, look for corroborating evidence:**
- University web forms: Some universities offer online graduate verification forms
- ORCID education records: GET https://pub.orcid.org/v3.0/{{orcid_id}}/educations — if the source is the institution (not self-asserted) → "supported"
- My eQuals (myequals.edu.au): Users can share verified qualification links → "supported"
- University staff pages: If the user appears on a faculty/staff page → "supported" for employment
- Credly / digital badges: Verified digital badges from institutions → "supported"
- If none of the above are available → "claimed" (1 pt, user's word only)

### Known Verification APIs

**Curtin University Graduation Check**
GET https://verify.curtin.edu.au/api/v1/graduation-check?name={{surname}}&studentId={{student_id}}
Response: {{"found": true, "program": "Bachelor of Science", "completionYear": 2019, "status": "Conferred"}}
If found=true → evidence_tier="confirmed"

**ORCID Education Records**
GET https://pub.orcid.org/v3.0/{{orcid_id}}/educations
Headers: Accept: application/json
Response includes education entries with a "source" field. If source.source-name != the person's own name,
the institution verified it → evidence_tier="supported". If self-asserted → evidence_tier="claimed".

### Investigation Workflow

1. Ask the user what qualifications they want verified (degree, certification, employment).
2. Check if there's a known API for the institution (see above). If so, query it directly.
3. If no API exists, look for corroborating evidence using the strategies above.
4. Assign the appropriate evidence tier based on what you found.
5. Submit via POST /v1/account/credentials.

### Endpoint: POST /v1/account/credentials

Authorization: Bearer <api_key>
Content-Type: application/json

Request body:
```json
{{
  "credentials": [
    {{
      "credential_type": "degree",
      "institution": "Curtin University",
      "title": "Bachelor of Science in Computer Science",
      "year": 2019,
      "evidence_tier": "confirmed",
      "evidence_data": {{"api_response": {{"found": true, "program": "Bachelor of Science", "completionYear": 2019}}}},
      "agent_notes": "Verified via Curtin graduation API on 2025-01-15"
    }}
  ]
}}
```

Rules:
- Max 20 credentials per request.
- Evidence tiers can only be upgraded on re-submit (confirmed > supported > claimed), never downgraded.
- Credentials are matched by (credential_type, institution, title) — duplicates update the existing record.
- Rate limited to 20 requests/hour.

## Learn More

These published guides explain each feature in depth:

- Platform overview: {settings.base_url}/what-is-lightpaper-org
- Document formats: {settings.base_url}/three-document-formats-post-essay-and-paper
- Quality scoring: {settings.base_url}/how-quality-scoring-works
- Author gravity: {settings.base_url}/author-gravity-a-trust-system-for-the-agentic-web
- API tutorial: {settings.base_url}/publishing-your-first-document-via-the-api
- MCP server: {settings.base_url}/using-the-mcp-server
- Search & SEO: {settings.base_url}/search-discovery-and-seo
- Authentication: {settings.base_url}/authentication-without-passwords
- Identity verification: {settings.base_url}/verifying-your-identity
- Markdown features: {settings.base_url}/markdown-code-highlighting-and-footnotes

## MCP Server

Connect to lightpaper.org via the Model Context Protocol for tool-based access.

### Remote (no install)

Connect directly — no package install needed:

URL: {settings.base_url}/mcp

Claude Desktop config:
```json
{{"mcpServers": {{"lightpaper": {{"url": "{settings.base_url}/mcp"}}}}}}
```

### Install from PyPI

```
pip install lightpaper-mcp
```

Claude Desktop config:
```json
{{"mcpServers": {{"lightpaper": {{"command": "lightpaper-mcp", "env": {{"LIGHTPAPER_API_KEY": "lp_free_your_key_here"}}}}}}}}
```

Or without an API key (interactive account creation):
```json
{{"mcpServers": {{"lightpaper": {{"command": "lightpaper-mcp"}}}}}}
```

Run standalone: `lightpaper-mcp` or `python -m lightpaper_mcp`

20 tools: publish, search, get, update, delete, list, account info, update account, gravity info, author profile, versions, credentials, auth (email + LinkedIn), verify (domain, LinkedIn, ORCID, credentials).
2 prompts: write-article, setup-account.

## Agent Discovery

- Google A2A agent card: {settings.base_url}/.well-known/agent.json
- OpenAI plugin manifest: {settings.base_url}/.well-known/ai-plugin.json
- MCP Registry: org.lightpaper/lightpaper-mcp

## OpenAPI

Full API specification: {settings.base_url}/v1/openapi.json
"""


@router.get("/sitemap.xml")
async def sitemap_xml(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .where(
            Document.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.quality_score >= 40,
        )
        .order_by(Document.updated_at.desc())
    )
    docs = result.scalars().all()

    urls = []
    for doc in docs:
        slug_url = f"{settings.base_url}/{doc.slug}" if doc.slug else f"{settings.base_url}/d/{doc.id}"
        lastmod = doc.updated_at.strftime("%Y-%m-%d") if doc.updated_at else ""
        urls.append(f"""  <url>
    <loc>{xml_escape(slug_url)}</loc>
    <lastmod>{xml_escape(lastmod)}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

    # Books
    book_result = await db.execute(
        select(Book)
        .where(
            Book.deleted_at.is_(None),
            Book.listed.is_(True),
        )
        .order_by(Book.updated_at.desc())
    )
    books = book_result.scalars().all()

    book_urls = []
    for book in books:
        book_url = f"{settings.base_url}/books/{book.slug}"
        lastmod = book.updated_at.strftime("%Y-%m-%d") if book.updated_at else ""
        book_urls.append(f"""  <url>
    <loc>{xml_escape(book_url)}</loc>
    <lastmod>{xml_escape(lastmod)}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    # Author profiles — accounts with a handle and at least one listed document
    author_result = await db.execute(
        select(Account.handle)
        .join(Document, Document.account_id == Account.id)
        .where(
            Account.handle.isnot(None),
            Account.deleted_at.is_(None),
            Document.listed.is_(True),
            Document.deleted_at.is_(None),
        )
        .group_by(Account.handle)
    )
    handles = [row[0] for row in author_result.all()]

    author_urls = []
    for handle in handles:
        author_urls.append(f"""  <url>
    <loc>{xml_escape(f"{settings.base_url}/@{handle}")}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{settings.base_url}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
{"".join(book_urls)}
{"".join(urls)}
{"".join(author_urls)}
</urlset>"""

    return Response(content=xml, media_type="application/xml")


@router.get("/v1/admin/indexing-report")
@limiter.limit("2/minute")
async def indexing_report(
    request: Request,
    auth=Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Check Google indexing status for all listed documents.

    Refreshes stale checks (>24h) via the URL Inspection API, then returns
    a full report of indexed vs. not-indexed documents.
    """
    from app.services.gsc import check_indexing_batch

    report = await check_indexing_batch(db)
    return report


@router.get("/og/{doc_id}.png")
@limiter.limit("30/minute")
async def og_image(request: Request, doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get reading time from current version
    ver_result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == doc.id,
            DocumentVersion.version == doc.current_version,
        )
    )
    version = ver_result.scalar_one_or_none()

    # Author name
    author_name = None
    if doc.authors:
        names = [a.get("name", a.get("handle", "")) for a in doc.authors]
        author_name = " & ".join(names[:3])

    # Badges from account verification + credentials
    badges = []
    if doc.account_id:
        acct_result = await db.execute(select(Account).where(Account.id == doc.account_id))
        account = acct_result.scalar_one_or_none()
        if account:
            cred_result = await db.execute(select(Credential).where(Credential.account_id == account.id))
            creds = cred_result.scalars().all()
            badges = get_gravity_badges(
                account.verified_domain,
                account.verified_linkedin,
                account.orcid_id,
                credentials=creds,
            )

    img_bytes = generate_og_image(
        title=doc.title,
        subtitle=doc.subtitle,
        quality_score=doc.quality_score,
        author_name=author_name,
        gravity_badges=badges,
        reading_time=version.reading_time if version else None,
        format=doc.format,
    )

    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/og/book_{book_id}.png")
@limiter.limit("30/minute")
async def book_og_image(request: Request, book_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    author_name = None
    if book.authors:
        names = [a.get("name", a.get("handle", "")) for a in book.authors]
        author_name = " & ".join(names[:3])

    img_bytes = generate_book_og_image(
        title=book.title,
        subtitle=book.subtitle,
        chapter_count=book.chapter_count,
        author_name=author_name,
        format=book.format,
    )

    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )
