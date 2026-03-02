# lightpaper.org — API Design Specification

## Design Philosophy

The API has one job: accept content, return a beautiful URL. Everything else supports that core or makes content discoverable.

- **REST over GraphQL** — The domain is simple (publish a document, get a URL). No relational graph to traverse.
- **Markdown first** — Every LLM produces Markdown natively. It is the lingua franca of AI agents.
- **One endpoint matters** — `POST /v1/publish` is the entire product. Everything else is auxiliary.
- **Content negotiation** — Same URL serves HTML (browsers) or JSON (agents) via `Accept` header.
- **Discovery built-in** — Agents find the platform through standard protocols without human help.

## Core Endpoint

### Publish a Document

```http
POST /v1/publish
Authorization: Bearer lp_live_abc123def456
Content-Type: application/json
Idempotency-Key: agent-session-2026-02-26-report-v1

{
  "title": "Straight Skeleton Algorithms for Hip Roof Generation",
  "subtitle": "A practical implementation guide for steel frame construction",
  "content": "# Introduction\n\nThe straight skeleton of a polygon...",
  "format": "markdown",
  "authors": [
    {"name": "Jane Smith", "handle": "jsmith"},
    {"name": "Sarah Chen", "handle": "sarahchen"}
  ],
  "metadata": {
    "tags": ["algorithms", "construction", "geometry"],
    "canonical_url": "https://example.com/research/straight-skeleton",
    "license": "CC-BY-4.0",
    "language": "en"
  },
  "options": {
    "slug": "straight-skeleton-hip-roofs",
    "listed": true,
    "og_image": "auto"
  }
}
```

**Response:**

```json
{
  "id": "doc_2xVn8kQ4mR",
  "url": "https://lightpaper.org/straight-skeleton-hip-roofs",
  "permanent_url": "https://lightpaper.org/d/doc_2xVn8kQ4mR",
  "version": 1,
  "created_at": "2026-02-26T10:30:00Z",
  "word_count": 3847,
  "reading_time_minutes": 15,
  "content_hash": "sha256:a1b2c3d4...",
  "quality_score": 78,
  "quality_breakdown": {
    "structure": 22,
    "substance": 21,
    "tone": 20,
    "attribution": 15
  },
  "quality_suggestions": [
    "Add 2-3 external references to improve attribution score"
  ],
  "author_gravity": 2,
  "author_gravity_badges": ["example.com ✓", "LinkedIn ✓"],
  "gravity_note": "Verify ORCID to reach Level 3 and increase search prominence by 40%"
}
```

That's the entire product in one request/response cycle. The quality score and suggestions help authors improve visibility.

## Full API Surface

### Publishing (core)

```
POST   /v1/publish                    # Create new document → returns permanent URL + quality score
PUT    /v1/documents/{id}             # Update existing document (creates new version, re-scores quality)
GET    /v1/documents/{id}             # Get document metadata + content (JSON)
GET    /v1/documents/{id}/versions    # List version history
DELETE /v1/documents/{id}             # Soft-delete (URL returns 410 Gone, not 404)
```

### Discovery

```
GET    /v1/search                     # Search documents: ?q=steel+frame&tags=construction&author=jsmith
GET    /v1/tags                       # List all tags with document counts [Planned]
GET    /v1/tags/{tag}                 # List documents with this tag [Planned]
GET    /v1/openapi.json               # OpenAPI 3.1 specification (standard for tool-using agents)
GET    /llms.txt                      # Machine-readable site description (courtesy signal)
GET    /.well-known/agent.json        # Google A2A Agent Card [Planned — Phase 2]
GET    /sitemap.xml                   # Auto-generated sitemap for search engines
GET    /robots.txt                    # Welcomes all crawlers

# Note: /.well-known/ai-plugin.json (OpenAI plugins) is NOT implemented.
# OpenAI plugins were deprecated 2025; Assistants API sunsets Aug 2026. Dead protocol.
```

### Content Negotiation

Any document URL supports content negotiation via `Accept` header:

```
GET /straight-skeleton-hip-roofs
Accept: text/html                     # Returns rendered HTML page (default for browsers)

GET /straight-skeleton-hip-roofs
Accept: application/json              # Returns structured JSON (document data + metadata)
```

The JSON response for content negotiation:

```json
{
  "id": "doc_2xVn8kQ4mR",
  "title": "Straight Skeleton Algorithms for Hip Roof Generation",
  "subtitle": "A practical implementation guide...",
  "content": "# Introduction\n\nThe straight skeleton...",
  "format": "markdown",
  "authors": [...],
  "metadata": {...},
  "word_count": 3847,
  "quality_score": 78,
  "created_at": "2026-02-26T10:30:00Z",
  "updated_at": "2026-02-26T10:30:00Z",
  "permanent_url": "https://lightpaper.org/d/doc_2xVn8kQ4mR"
}
```

### Author Profiles [Planned]

> **[Planned]** — Not yet implemented.

```
GET    /v1/authors/{handle}           # Author profile (bio, verified badges, stats)
GET    /v1/authors/{handle}/documents # All listed documents by this author
GET    /v1/authors/{handle}/feed.xml  # RSS/Atom feed for this author
```

### Collections [Planned]

> **[Planned]** — Not yet implemented.

```
POST   /v1/collections               # Create a collection (e.g., "Research Series")
PUT    /v1/collections/{id}           # Update collection metadata
POST   /v1/collections/{id}/documents # Add document to collection
GET    /v1/collections/{id}           # List documents in collection
```

### Authentication

```
POST   /v1/auth/email                 # Send OTP code to email, returns session_id
POST   /v1/auth/verify                # Verify OTP code, returns account + API key
POST   /v1/auth/linkedin              # Start LinkedIn OAuth, returns authorization URL
GET    /v1/auth/linkedin/callback     # LinkedIn OAuth callback (browser redirect)
GET    /v1/auth/linkedin/poll         # Poll for LinkedIn OAuth completion
```

### Account and Ownership

```
POST   /v1/account                    # Create account (Firebase Auth token required)
GET    /v1/account                    # Account info, usage stats, verified identities
GET    /v1/account/documents          # List all documents for this account
GET    /v1/account/export             # Export all content as ZIP [Planned]
DELETE /v1/account                    # Hard-delete account + all content (GDPR)
```

### API Keys (scoped to account)

```
POST   /v1/account/keys               # Create new API key
GET    /v1/account/keys               # List active keys (prefix only, not full key)
DELETE /v1/account/keys/{prefix}       # Revoke a key (documents are NOT deleted)
POST   /v1/account/keys/{prefix}/rotate # Rotate key — new key, old key revoked [Planned]
```

### Author Verification

```
POST   /v1/account/verify/domain       # Start domain verification → returns DNS TXT record to add
GET    /v1/account/verify/domain/check # Poll: is the DNS TXT record present? → confirms Level 1
GET    /v1/account/verify/linkedin     # Redirect to LinkedIn OAuth flow [Planned]
POST   /v1/account/verify/orcid        # Link ORCID iD [Planned]
GET    /v1/account/gravity             # Current gravity level + badges + what's needed for next level
```

### Onboarding Agent (MCP Tool)

The `setup_author_identity` MCP tool orchestrates the full verification flow. It calls the above endpoints in sequence, auto-detects registrar from email domain, generates exact copy-paste instructions, and polls for completion.

```bash
# Via MCP (Claude Code, any MCP-compatible agent):
use tool: setup_author_identity
→ Walks through all four levels
→ Auto-detects domain from account email
→ Generates DNS TXT record
→ Opens LinkedIn OAuth URL
→ Guides ORCID setup if applicable
→ Returns: "Level 3 complete — ORCID ✓ example.com ✓ LinkedIn ✓"
```

The tool is also exposed as a web flow at `lightpaper.org/account/setup` — the same logic, presented as a step-by-step UI immediately after account creation.

### Feeds [Planned]

> **[Planned]** — Not yet implemented.

```
GET    /v1/authors/{handle}/feed.xml  # RSS/Atom feed for an author
GET    /v1/tags/{tag}/feed.xml        # RSS/Atom feed for a tag
GET    /feed.xml                      # Global feed (recent high-quality documents)
```

### Analytics [Planned]

> **[Planned]** — Not yet implemented.

```
GET    /v1/documents/{id}/analytics   # View count, referrers, geography
GET    /v1/documents/{id}/citations   # Documents that cite this one
```

## Search API

Search is a Phase 1 feature. Without it, agents and humans cannot find content.

```http
GET /v1/search?q=steel+frame+construction&tags=construction,engineering&author=jsmith&min_quality=40&sort=relevance&limit=20&offset=0
```

**Response:**

```json
{
  "results": [
    {
      "id": "doc_2xVn8kQ4mR",
      "title": "Straight Skeleton Algorithms for Hip Roof Generation",
      "subtitle": "A practical implementation guide...",
      "url": "https://lightpaper.org/straight-skeleton-hip-roofs",
      "authors": [{"name": "Jane Smith", "handle": "jsmith"}],
      "tags": ["algorithms", "construction", "geometry"],
      "quality_score": 78,
      "word_count": 3847,
      "created_at": "2026-02-26T10:30:00Z",
      "snippet": "...the straight skeleton provides the ridge and hip lines needed for..."
    }
  ],
  "total": 47,
  "limit": 20,
  "offset": 0
}
```

**Parameters:**

| Param | Type | Description |
|-------|------|------------|
| `q` | string | Full-text search query (PostgreSQL tsvector + pg_trgm) |
| `tags` | string | Comma-separated tag filter |
| `author` | string | Filter by author handle |
| `min_quality` | int | Minimum quality score (default: 40 for indexed content) |
| `sort` | string | `relevance` (default), `recent`, `quality`, `views` |
| `limit` | int | Results per page (max 100, default 20) |
| `offset` | int | Pagination offset |

## Content Formats

### Markdown (primary — recommended)

Standard CommonMark with extensions:

| Extension | Syntax | Use Case |
|-----------|--------|----------|
| GFM Tables | `\| col \|` | Data presentation |
| Fenced code blocks | ` ```python ` | Code with syntax highlighting |
| LaTeX math | `$inline$` and `$$block$$` | Technical/scientific content |
| Footnotes | `[^1]` | Academic references |
| Admonitions | `:::warning` | Callouts, notes, tips |
| Mermaid diagrams | ` ```mermaid ` | Flowcharts, sequence diagrams |
| Task lists | `- [x]` | Checklists |
| Images | `![alt](url "caption")` | Inline images with captions |

### Inline Media

> **[Planned]** — Media upload endpoint not yet implemented.

Images and video can be included in Markdown content:

```markdown
![Roof skeleton diagram](https://your-bucket.storage.googleapis.com/doc_xxx/skeleton.png "Figure 1: Straight skeleton of an L-shaped polygon")

<video src="https://your-bucket.storage.googleapis.com/doc_xxx/animation.mp4" controls></video>

<!-- YouTube/Vimeo embeds rendered as clean iframes -->
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Media upload endpoint (Pro tier) [Planned]:

```http
POST /v1/media
Authorization: Bearer lp_live_xxx
Content-Type: multipart/form-data

file=@skeleton.png
```

Response:
```json
{
  "url": "https://your-bucket.storage.googleapis.com/acct_xxx/skeleton.png",
  "content_type": "image/png",
  "size_bytes": 48392
}
```

### HTML (secondary)

Pre-rendered HTML, sanitized server-side. Allowlisted tags only (no `<script>`, `<iframe>` except YouTube/Vimeo, `onclick`, `javascript:` URLs). `<figure>`, `<figcaption>`, `<video>`, `<img>` supported for media.

### Structured JSON (advanced) [Planned]

> **[Planned]** — Not yet implemented.

For agents that want precise control over layout:

```json
{
  "format": "structured",
  "blocks": [
    {"type": "heading", "level": 1, "text": "Introduction"},
    {"type": "paragraph", "text": "The straight skeleton..."},
    {"type": "code", "language": "python", "content": "def skeleton(polygon):..."},
    {"type": "math", "display": "block", "tex": "\\sum_{i=0}^{n} x_i"},
    {"type": "image", "url": "https://...", "alt": "Diagram", "caption": "Figure 1"},
    {"type": "video", "url": "https://...", "caption": "Build animation"}
  ]
}
```

## Authentication

### Account-Based Auth

Authentication is account-based, not key-based. API keys are scoped credentials owned by accounts.

```
Account (Firebase Auth)
  ├── API Key: lp_live_abc123...  (production)
  ├── API Key: lp_test_def456...  (test)
  └── Documents owned by account (not by key)
```

Revoking a key does NOT delete documents. Creating a new key does NOT lose access to existing documents. This solves the "fragile key" problem where losing an API key means losing access to content.

### Two Tiers

| Tier | Auth | Gravity | Capabilities |
|------|------|---------|-------------|
| Free Account | `Bearer lp_free_xxx` | Level 0–3 | 100 docs/month. Permanent URLs. Full gravity (verification-dependent). Basic analytics. 1 key. |
| Pro Account | `Bearer lp_live_xxx` | Level 0–3 | Unlimited docs. Custom slugs. Full analytics. Custom domains. Up to 3 keys. |

**Every document requires an authenticated author.** There is no anonymous publishing. A human creates an account, verifies their identity, generates an API key, and delegates that key to their agent or automation. Every document published with that key is attributed to that human — they are the author of record. The agent is the tool.

This is the standard professional model: a social media manager posts on behalf of a CEO; the CEO is responsible. A PR firm sends emails on behalf of a founder; the founder is accountable. On lightpaper.org, the account holder is always the author — regardless of who or what typed the words.

### Key Design

```
lp_free_abc123def456ghi789jkl012    (free tier key)
lp_live_abc123def456ghi789jkl012    (production key)
lp_test_abc123def456ghi789jkl012    (test key — not indexed, auto-expires)
```

Prefixed so agents instantly know which environment they're targeting. Test keys let agents iterate on formatting without polluting the namespace.

### Authentication Flows

**Email OTP** (primary — works for any agent):
```
POST /v1/auth/email       → sends 6-digit code to email, returns session_id
POST /v1/auth/verify      → verifies code, returns account + API key
```

**LinkedIn OAuth** (for users with LinkedIn):
```
POST /v1/auth/linkedin           → returns authorization URL + session_id
GET  /v1/auth/linkedin/callback  → OAuth callback (browser redirect)
GET  /v1/auth/linkedin/poll      → agent polls for completion, returns API key
```

**API key** (returning users):
```
Authorization: Bearer lp_free_xxx
```

**Why not OAuth for the publish flow?** OAuth requires redirect flows that make no sense for headless agents. API keys are the right abstraction for the publish flow. Email OTP and LinkedIn OAuth handle the account creation layer.

## Agent Discovery

### MCP Server (Primary — Phase 1)

Native integration for Claude Code and any MCP-compatible agent (8,600+ server ecosystem, Linux Foundation standard):

```bash
npx @lightpaper/mcp-server
```

Tools exposed:
- `publish_lightpaper` — Publish a document, return permanent URL
- `search_lightpapers` — Search by query, tags, author
- `get_lightpaper` — Retrieve a document by ID
- `update_lightpaper` — Update an existing document
- `list_my_lightpapers` — List all documents for the authenticated account

### OpenAPI Spec (Phase 1)

Full OpenAPI 3.1 spec at `/v1/openapi.json`. Standard for any tool-using agent that supports OpenAPI tool definitions.

### Google A2A Agent Card [Planned]

Served at `/.well-known/agent.json`. Google's A2A protocol (v0.3, 50+ partners including Salesforce, SAP, Deloitte) enables agent-to-agent discovery. MCP = agent accesses tools. A2A = agent discovers lightpaper.org as a collaborator.

```json
{
  "name": "lightpaper.org Publisher",
  "description": "Publish permanent, beautiful documents via API. Accepts Markdown, returns shareable URLs.",
  "url": "https://lightpaper.org",
  "version": "1.0.0",
  "skills": [
    {"id": "publish", "name": "Publish Document", "description": "Publish Markdown, get permanent URL"},
    {"id": "search", "name": "Search Documents", "description": "Search the lightpaper.org knowledge base"}
  ],
  "authentication": {"schemes": ["Bearer"]}
}
```

### llms.txt (Courtesy Signal)

Served at `https://lightpaper.org/llms.txt`. 844K sites deploy `llms.txt`; no major AI platform currently reads it. We serve it because it costs nothing and the standard may mature. Not a core discovery mechanism.

```
# lightpaper.org
> API-first publishing platform for permanent, beautiful documents.

## API
POST /v1/publish — Publish a document. Returns permanent URL.
GET /v1/search — Search documents by query, tags, author.
GET /v1/openapi.json — Full OpenAPI specification.

## Auth
Bearer lp_live_xxx — Create account at https://lightpaper.org/account

## MCP
npx @lightpaper/mcp-server
```

## Quality Scoring and Author Gravity

Every document is scored on two orthogonal dimensions at publish time: content quality and author gravity. Both are returned in the API response and both are transparent.

### Content Quality Score (0-100)

| Dimension | Max | Signals |
|-----------|-----|---------|
| Structure (0-25) | 25 | Headings, organised flow, not wall-of-text, paragraph variety |
| Substance (0-25) | 25 | Word count (300 min, 1000+ ideal), information density, specific claims |
| Tone (0-25) | 25 | Professional register, not inflammatory, not clickbait, consistent |
| Attribution (0-25) | 25 | External links, references section, citations, evidence for claims |

### Author Gravity Level (0-3)

| Level | Verification | Gravity Multiplier | Featured Threshold |
|-------|-------------|-------------------|-------------------|
| 0 | Email only | 1.0× | Quality ≥ 70 |
| 1 | + Domain DNS TXT | 1.1× | Quality ≥ 68 |
| 2 | + LinkedIn OAuth | 1.25× | Quality ≥ 65 |
| 3 | + ORCID | 1.4× | Quality ≥ 60 |

### Visibility Tiers

| Quality Score | Effect |
|--------------|--------|
| < 40 | Published but `noindex`. Hidden from search and explore. Direct URL only. Equal for all gravity levels. |
| ≥ 40 | Indexed. Appears in search API and on author page. Search ranking = relevance × quality × gravity multiplier. |
| ≥ featured threshold | Featured-eligible. Appears in explore/curated feeds. Threshold varies by gravity level (see table above). |

A Level 3 author's quality-65 paper is featured. A Level 0 author's quality-65 paper is indexed but not featured. The content isn't worse — the author simply hasn't established verifiable identity yet.

### Key Principles

- **Never refuse valid content.** The API always publishes (returns 201). Quality and gravity affect visibility, not access.
- **Transparent.** Full quality breakdown and current gravity level returned to author. No black-box.
- **Actionable.** Two paths to improve: edit the content (raises quality score) or verify identity (raises gravity).
- **Improvable.** Quality score recalculated on every update. Gravity updates immediately when verification completes.

## Idempotency [Planned]

AI agents retry. Network calls fail. Same workflow might run twice.

```http
Idempotency-Key: agent-session-2026-02-26-report-v1
```

- Server stores `(api_key, idempotency_key) → response` for 24 hours in Memorystore Redis
- Duplicate request returns stored response (HTTP 200, not 201)
- Key is optional, free-form string, max 256 chars
- Without key, every POST creates a new document

## Rate Limits

| Tier | Publish | Read API | Burst |
|------|---------|----------|-------|
| Free | 100/month, 10/hour | 1,000/hour | 10/second |
| Pro | Unlimited, 60/hour | 10,000/hour | 30/second |

Headers on every response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1708950000
Retry-After: 30        (only on 429)
```

## URL Structure

Every document gets two URLs:

| Type | Example | Properties |
|------|---------|------------|
| Permanent ID | `lightpaper.org/d/doc_2xVn8kQ4mR` | Never changes. Based on internal ID. |
| Slug | `lightpaper.org/straight-skeleton-hip-roofs` | Human-readable. Can redirect on slug change. |

Other URL patterns:

| URL | Purpose |
|-----|---------|
| `lightpaper.org/@jsmith` | Author profile page |
| `lightpaper.org/tag/construction` | Tag browsing page |
| `lightpaper.org/d/doc_xxx/v/1` | Specific version |
| `lightpaper.org/d/doc_xxx/diff/1..2` | Diff view |

**ID generation**: KSUID-style — URL-safe, sortable by creation time, collision-resistant, ~11 characters.

## Content Versioning

Content is **versioned, not immutable**:

- Every edit creates a new version with its own content hash
- URL always serves latest version
- Previous versions at `lightpaper.org/d/doc_xxx/v/1`
- Diff view at `lightpaper.org/d/doc_xxx/diff/1..2`
- SHA-256 content hash stored per version for integrity verification
- Quality score recalculated on each version

## Deletion Policy

- `DELETE /v1/documents/{id}` → soft delete
- URL returns HTTP **410 Gone** with tombstone page
- URL is **never reassigned** to different content
- Content retained 90 days for abuse investigation, then hard-deleted
- Content hash and metadata retained permanently in audit log
- `DELETE /v1/account` → GDPR hard-delete of all content (no 90-day retention)

## Agent Tool Definition

The MCP tool definition:

```python
{
    "name": "publish_lightpaper",
    "description": "Publish a document to lightpaper.org and get a permanent shareable URL. Returns quality score.",
    "parameters": {
        "title": {"type": "string", "description": "Document title"},
        "content": {"type": "string", "description": "Markdown content"},
        "subtitle": {"type": "string", "description": "Optional subtitle"},
        "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags for discovery"}
    }
}
```

Or as a simple curl:

```bash
curl -X POST https://lightpaper.org/v1/publish \
  -H "Authorization: Bearer lp_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Research", "content": "# Hello\n\nWorld.", "metadata": {"tags": ["research"]}}'
```

## Error Responses

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 30 seconds.",
    "retry_after": 30
  }
}
```

Standard HTTP status codes:
- `201 Created` — document published
- `200 OK` — idempotent replay or update
- `400 Bad Request` — invalid content/format (below 300 word minimum, no heading)
- `401 Unauthorized` — missing or invalid API key
- `404 Not Found` — document doesn't exist
- `410 Gone` — document was deleted
- `429 Too Many Requests` — rate limited
- `500 Internal Server Error` — server issue

## API Versioning

URL-based: `/v1/publish`. Breaking changes get `/v2/`. Non-breaking additions go in current version. Old versions supported minimum 2 years after deprecation.
