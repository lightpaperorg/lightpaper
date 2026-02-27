# lightpaper.org — Technical Architecture

## System Overview

```
                    Cloud CDN + Cloud Load Balancing
                    (cache HTML + OG images at edge)
                         │
              ┌──────────┴──────────────────────────────────────┐
              │          │              │                         │
              ▼          ▼              ▼                         ▼
         GET /{slug}   GET /og/{id}  POST /v1/publish    GET /v1/search
         (read path)   (OG image)   (write path)         (discovery)
              │          │              │                         │
              ▼          ▼              ▼                         ▼
              ┌──────────────────────────────────────────────────┐
              │  Application Server (Cloud Run)                  │
              │  FastAPI (Python) — Docker container             │
              │                                                  │
              │  ├─ Publish API + quality scoring                │
              │  ├─ Render pipeline (Markdown → HTML)            │
              │  ├─ Content negotiation (HTML or JSON)           │
              │  ├─ OG image generation (Pillow)                 │
              │  ├─ Search API (full-text + tags)                │
              │  ├─ Author profiles + verification               │
              │  ├─ MCP server endpoint                          │
              │  └─ Discovery (MCP, OpenAPI, A2A, llms.txt)      │
              └──────────┬────────────────────┬─────────────────┘
                         │                    │
              ┌──────────┴───────┐   ┌───────┴──────────┐
              │                  │   │                    │
              ▼                  ▼   ▼                    ▼
       ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
       │  Cloud SQL   │  │  Memorystore │  │  Cloud Storage   │
       │  PostgreSQL  │  │  Redis       │  │  ────────────    │
       │  ─────────── │  │  ──────────  │  │  OG images       │
       │  documents   │  │  rate limits │  │  media uploads   │
       │  versions    │  │  idempotency │  │  content exports │
       │  accounts    │  │  cache       │  │                  │
       │  api_keys    │  │              │  │                  │
       │  quality     │  │              │  │                  │
       │  authors     │  │              │  │                  │
       │  analytics   │  │              │  │                  │
       │  search idx  │  │              │  │                  │
       └─────────────┘  └──────────────┘  └──────────────────┘
              │
              ▼
       ┌─────────────┐
       │  Firebase    │
       │  Auth        │
       │  ──────────  │
       │  Google SSO  │
       │  email/pass  │
       │  LinkedIn    │
       └─────────────┘
```

## Why Python / FastAPI

| Factor | FastAPI (Python) | Next.js (Node) | Go/Rust | CF Workers |
|--------|-----------------|-----------------|---------|------------|
| Markdown rendering | Excellent ecosystem | Excellent (unified/remark) | Limited | Very limited |
| KaTeX server-side | Yes (subprocess/binding) [Planned] | Native (katex npm) | Bindings | Not practical |
| Pygments highlighting | Via subprocess or tree-sitter | Native | tree-sitter | Limited |
| Mermaid SVG | mermaid-cli subprocess [Planned] | mermaid-cli subprocess | Harder | Not possible |
| Dev speed | Very fast | Fast | Slower | Fast but constrained |
| Agent tooling | Claude/GPT produce Python natively | Good | Moderate | Moderate |
| Cloud Run compat | Excellent (Docker) | Excellent | Excellent | N/A |

**The critical insight:** The rendering pipeline (Markdown → HTML with syntax highlighting, math, diagrams) is the complex part. Python has the richest ecosystem for this. Raw throughput doesn't matter because Cloud CDN serves 99%+ of reads.

## Infrastructure — Google Cloud

| Component | Service | Spec | Cost/month |
|-----------|---------|------|------------|
| Application server | Cloud Run | 2 vCPU, 4GB RAM, auto-scale 0-10 | ~$20-40 |
| Database | Cloud SQL for PostgreSQL | db-f1-micro (dev), db-custom-2-4096 (prod) | ~$30-50 |
| Cache | Memorystore for Redis [Planned] | Basic tier, 1GB | ~$15 |
| CDN | Cloud CDN + Cloud Load Balancing | Global edge, Google-managed SSL | ~$5-10 |
| Object storage | Cloud Storage [Planned] | Standard class, multi-region | ~$1-5 |
| Auth | Firebase Auth | Google sign-in + email/password | Free (< 50K users) |
| Search | Cloud SQL full-text | tsvector + pg_trgm (in PostgreSQL) | $0 (included) |
| Monitoring | Cloud Monitoring + Logging | Metrics, alerting, log analysis | Free tier |
| SSL | Google-managed certificates | Auto-renew, free | $0 |
| **Total** | | | **~$70-120/mo** |

Cloud Run scales to zero during low traffic. Cloud CDN absorbs reads. Total cost stays under $100/mo until significant scale.

## Database Schema

```sql
-- Accounts (Firebase Auth backed)
CREATE TABLE accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid    TEXT UNIQUE NOT NULL,
    handle          TEXT UNIQUE,                -- @handle for profile URLs
    display_name    TEXT,
    bio             TEXT,
    avatar_url      TEXT,
    tier            TEXT NOT NULL DEFAULT 'free',   -- free, pro, team
    verified_domain TEXT,                        -- e.g. "example.com" (Level 1)
    verified_linkedin BOOLEAN DEFAULT false,     -- (Level 2)
    orcid_id        TEXT,                        -- "0000-0002-1825-0097" (Level 3)
    gravity_level   INTEGER NOT NULL DEFAULT 0, -- 0-3, computed from verification fields
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- gravity_level is derived (could be a generated column):
-- 0: no domain, no linkedin, no orcid
-- 1: verified_domain IS NOT NULL
-- 2: verified_domain IS NOT NULL AND verified_linkedin = true
-- 3: verified_domain IS NOT NULL AND verified_linkedin = true AND orcid_id IS NOT NULL

-- API keys (scoped to accounts)
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    key_hash        TEXT NOT NULL UNIQUE,     -- bcrypt hash
    key_prefix      TEXT NOT NULL,            -- first 8 chars for identification
    label           TEXT,                     -- user-friendly name
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ
);

-- Documents
CREATE TABLE documents (
    id              TEXT PRIMARY KEY,           -- doc_2xVn8kQ4mR (KSUID)
    account_id      UUID REFERENCES accounts(id),  -- NULL for anonymous
    slug            TEXT UNIQUE,
    title           TEXT NOT NULL,
    subtitle        TEXT,
    format          TEXT NOT NULL DEFAULT 'markdown',
    current_version INTEGER NOT NULL DEFAULT 1,
    authors         JSONB DEFAULT '[]',         -- [{name, handle}] — all human, no AI disclosure required
    metadata        JSONB DEFAULT '{}',
    listed          BOOLEAN DEFAULT true,
    quality_score   INTEGER,                   -- 0-100 composite score
    quality_detail  JSONB,                     -- {structure, substance, tone, attribution}
    author_gravity  INTEGER NOT NULL DEFAULT 0, -- snapshot of account gravity_level at publish time
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
-- author_gravity is snapshotted at publish so historical documents reflect the gravity
-- the author had when they published — this prevents retroactive gravity inflation.

-- Full-text search vector (auto-updated via trigger)
ALTER TABLE documents ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(subtitle, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(metadata->>'tags', '')), 'C')
    ) STORED;

CREATE INDEX idx_documents_search ON documents USING GIN(search_vector);
CREATE INDEX idx_documents_tags ON documents USING GIN((metadata->'tags'));

-- Document versions
CREATE TABLE document_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    content         TEXT NOT NULL,
    content_hash    TEXT NOT NULL,       -- sha256 of raw content
    rendered_html   TEXT,                -- pre-rendered (cached)
    word_count      INTEGER,
    reading_time    INTEGER,             -- minutes
    toc             JSONB,               -- auto-generated table of contents
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(document_id, version)
);

-- Full-text search on content (for search API)
ALTER TABLE document_versions ADD COLUMN content_search tsvector;
CREATE INDEX idx_versions_content_search ON document_versions USING GIN(content_search);

-- Citations (document A references document B)
CREATE TABLE citations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_doc_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_doc_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(source_doc_id, target_doc_id)
);

-- Analytics events [Planned]
CREATE TABLE analytics_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    event_type      TEXT NOT NULL,            -- 'view', 'share', 'embed'
    referrer        TEXT,
    country         TEXT,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_documents_slug ON documents(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_documents_account ON documents(account_id);
CREATE INDEX idx_documents_quality ON documents(quality_score) WHERE deleted_at IS NULL AND listed = true;
CREATE INDEX idx_documents_created ON documents(created_at DESC) WHERE deleted_at IS NULL AND listed = true;
CREATE INDEX idx_versions_document ON document_versions(document_id, version);
CREATE INDEX idx_analytics_document ON analytics_events(document_id, created_at);
CREATE INDEX idx_citations_target ON citations(target_doc_id);

-- Trigram index for fuzzy search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);
```

## Rendering Pipeline

```
Request: GET /straight-skeleton-hip-roofs
    │
    ├── Check Accept header
    │     ├── application/json → Return structured JSON (content negotiation)
    │     └── text/html (default) → Continue to render pipeline
    │
    ├── Cloud CDN cache hit? → Return cached HTML (< 50ms globally)
    │
    ├── CDN miss → Cloud Run application server
    │       │
    │       ├── Load document + current version from Cloud SQL
    │       ├── rendered_html cached in DB? → Use it
    │       ├── Otherwise: full render pipeline
    │       │       │
    │       │       ├── Markdown → HTML (markdown-it + extensions)
    │       │       ├── Syntax highlighting (Pygments)
    │       │       ├── LaTeX → MathML/SVG (KaTeX) [Planned]
    │       │       ├── Mermaid → SVG (mermaid-cli) [Planned]
    │       │       ├── Images → <figure> + <figcaption> [Planned]
    │       │       ├── Video → <video> or clean iframe embed [Planned]
    │       │       ├── Generate TOC from headings
    │       │       ├── Wrap in semantic HTML template:
    │       │       │     - <article> + <section> structure
    │       │       │     - Open Graph meta tags
    │       │       │     - Twitter Card meta tags
    │       │       │     - JSON-LD Schema.org/Article
    │       │       │     - Inline CSS (monochrome "lightpaper" design)
    │       │       │     - Dark mode via prefers-color-scheme
    │       │       │     - Reading progress bar (< 1KB vanilla JS) [Planned]
    │       │       └── Cache rendered HTML in DB + CDN headers
    │       │
    │       └── Return HTML with Cache-Control: public, max-age=3600, s-maxage=86400
    │
    └── Complete semantic HTML document. Zero JS framework dependencies.
```

## The "Lightpaper" Design Language

The design is monochrome by intent. The content provides the colour. Everything else is black, white, and grey.

### Colour Palette

| Property | Light Mode | Dark Mode |
|----------|-----------|-----------|
| Background | `#FFFFFF` (pure white) | `#111827` (near-black) |
| Headings | `#111827` (near-black) | `#F9FAFB` (near-white) |
| Body text | `#374151` (dark grey) | `#D1D5DB` (light grey) |
| Secondary text | `#6B7280` (medium grey) | `#9CA3AF` (medium grey) |
| Borders/dividers | `#E5E7EB` (light grey) | `#374151` (dark grey) |
| Links | `#374151` underlined (no blue) | `#D1D5DB` underlined |
| Code background | `#F9FAFB` (barely-there grey) | `#1F2937` (dark grey) |

**No colour accents.** No brand colours on the reading page. The content — images, diagrams, code — provides any colour. The chrome is invisible.

### Typography

| Property | Value | Rationale |
|----------|-------|-----------|
| Body font | **Inter** | Clean, modern, excellent screen rendering, high x-height |
| Code font | **JetBrains Mono** | Ligatures, clear distinction from body |
| Body size | 18px / 1.75 line-height | Optimized for sustained reading |
| Max width | 680px | ~65 chars per line (optimal readability) |
| Heading scale | 2.0 / 1.5 / 1.25 / 1.1 | Clear hierarchy |
| Paragraph spacing | 1.5em | Generous breathing room |

All fonts: `font-display: swap` with system font fallback. Zero layout shift.

### Page Layout

```
┌─────────────────────────────────────────────┐
│                                             │
│  lightpaper.org [wordmark — subtle, grey]   │
│                                             │
│  Title (H1, Inter, #111827)                 │
│  Subtitle (Inter, #6B7280)                  │
│  @author · Feb 26, 2026 · 15 min read      │
│  Quality: 78/100 · CC-BY-4.0               │
│                                             │
│  ─────────────────────────────────          │
│                                             │
│  Table of Contents (collapsible)            │
│                                             │
│  <article>                                  │
│    <section>                                │
│      Body content...                        │
│      - Typography optimized for reading     │
│      - Code blocks (Pygments, JetBrains Mono)  │
│      - Math rendered inline (KaTeX) [Planned]         │
│      - <figure><img><figcaption>            │
│      - <video> with clean controls          │
│      - Tables with clean monochrome style   │
│      - Mermaid diagrams as inline SVG [Planned]       │
│    </section>                               │
│  </article>                                 │
│                                             │
│  ─────────────────────────────────          │
│                                             │
│  Cited by: 3 documents                      │
│                                             │
│  Published on lightpaper.org                │
│  Permanent link: lightpaper.org/d/doc_xxx   │
│  Content hash: sha256:a1b2c3...             │
│  [Publish yours via API →]                  │
│                                             │
└─────────────────────────────────────────────┘
```

**No UI chrome.** No navigation bars, no sidebars, no cookie banners, no sign-up prompts. Just the content.

### Media Handling

**Images:**
- Rendered as `<figure>` with optional `<figcaption>`
- Full content width (680px max), responsive
- `loading="lazy"` for below-fold images
- Dimensions set in HTML to prevent CLS
- Served from Cloud Storage via Cloud CDN

**Video:**
- HTML5 `<video>` tag with `controls` attribute for direct uploads
- YouTube/Vimeo URLs auto-converted to clean, borderless `<iframe>` embeds
- No autoplay. Respects user control.

### Inline CSS

All styles are inlined in the `<head>` — no external stylesheet requests. The entire CSS is < 3KB. This ensures:
- Zero render-blocking resources
- Works in email clients (some render inline CSS)
- Content renders identically without CDN
- First paint is immediate

## Semantic HTML Structure

Every page is structured for four audiences: humans, search engines, agents, LLM training crawlers.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Straight Skeleton Algorithms for Hip Roof Generation — lightpaper.org</title>

  <!-- Open Graph -->
  <meta property="og:title" content="Straight Skeleton Algorithms for Hip Roof Generation">
  <meta property="og:description" content="A practical implementation guide...">
  <meta property="og:image" content="https://lightpaper.org/og/doc_2xVn8kQ4mR.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:url" content="https://lightpaper.org/straight-skeleton-hip-roofs">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="lightpaper.org">
  <meta name="twitter:card" content="summary_large_image">

  <!-- JSON-LD Schema.org/Article -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Straight Skeleton Algorithms for Hip Roof Generation",
    "description": "A practical implementation guide for steel frame construction",
    "author": [
      {"@type": "Person", "name": "Jane Smith", "url": "https://lightpaper.org/@jsmith"},
      {"@type": "Person", "name": "Claude", "description": "AI assistant"}
    ],
    "datePublished": "2026-02-26T10:30:00Z",
    "publisher": {"@type": "Organization", "name": "lightpaper.org", "url": "https://lightpaper.org"},
    "mainEntityOfPage": "https://lightpaper.org/straight-skeleton-hip-roofs",
    "wordCount": 3847,
    "keywords": ["algorithms", "construction", "geometry"],
    "license": "https://creativecommons.org/licenses/by/4.0/"
  }
  </script>

  <style>/* Inline CSS — monochrome design, < 3KB */</style>
</head>
<body>
  <header>
    <a href="/">lightpaper.org</a>
  </header>

  <article>
    <header>
      <h1>Straight Skeleton Algorithms for Hip Roof Generation</h1>
      <p class="subtitle">A practical implementation guide for steel frame construction</p>
      <p class="meta">
        <a href="/@jsmith">@jsmith</a> · Feb 26, 2026 · 15 min read
      </p>
    </header>

    <nav class="toc" aria-label="Table of contents">
      <!-- Auto-generated from headings -->
    </nav>

    <section class="content">
      <!-- Rendered Markdown → semantic HTML -->
      <h2>Introduction</h2>
      <p>The straight skeleton of a polygon...</p>
      <figure>
        <img src="..." alt="Skeleton diagram" width="680" height="400" loading="lazy">
        <figcaption>Figure 1: Straight skeleton of an L-shaped polygon</figcaption>
      </figure>
    </section>
  </article>

  <footer>
    <p>Published on <a href="/">lightpaper.org</a></p>
    <p>Permanent link: <a href="/d/doc_2xVn8kQ4mR">lightpaper.org/d/doc_2xVn8kQ4mR</a></p>
    <p>Content hash: sha256:a1b2c3...</p>
  </footer>

  <script>/* < 5KB: dark mode toggle, reading progress bar, TOC scroll spy */</script>
</body>
</html>
```

**Key properties:**
- Server-side rendered (Pillow) — content is in the HTML source, not JS-rendered
- Semantic elements: `<article>`, `<section>`, `<header>`, `<nav>`, `<figure>`, `<figcaption>`, `<footer>`
- JSON-LD structured data on every page
- Total JS < 5KB: dark mode, reading progress, TOC. Content renders without JS.
- No tracking scripts. Analytics via server-side event logging only.
- No external stylesheets. Inline CSS only.

## Discovery Infrastructure

### llms.txt

Served at `https://lightpaper.org/llms.txt`. Describes the platform for LLMs that encounter the domain.

### robots.txt

```
User-agent: *
Allow: /

Sitemap: https://lightpaper.org/sitemap.xml
```

Welcomes ALL crawlers. No Disallow rules. Training crawlers (CCBot, GPTBot, Applebot, etc.) are explicitly welcome — being in training data is distribution.

### sitemap.xml

Auto-generated, updated on publish/update/delete. Includes:
- All listed documents with quality_score >= 40
- Author profile pages
- Tag browsing pages
- Updated `<lastmod>` timestamps

### OpenAPI Spec

Full OpenAPI 3.1 at `/v1/openapi.json`. Standard for any tool-using agent.

### Google A2A Agent Card [Planned — Phase 2]

At `/.well-known/agent.json`. Google's A2A protocol for agent-to-agent discovery. Complements MCP (MCP = tool access, A2A = agent collaboration discovery).

> **Note:** `/.well-known/ai-plugin.json` (OpenAI plugins) is NOT served. OpenAI plugins were deprecated 2025; the Assistants API sunsets August 2026. Dead protocol — not implemented.

## Quality Scoring Pipeline

```
POST /v1/publish
    │
    ├── Parse content (Markdown → AST)
    │
    ├── Score structure (0-25)
    │     ├── Has headings? (+5 per heading level used, max 15)
    │     ├── Multiple sections? (+5)
    │     └── Paragraph variety (not wall-of-text)? (+5)
    │
    ├── Score substance (0-25)
    │     ├── Word count: 300-500 (+5), 500-1000 (+10), 1000-2000 (+15), 2000+ (+20)
    │     ├── Information density (unique terms / total terms) (+5)
    │     └── Specific claims, data, numbers present? (+5 if detected)
    │
    ├── Score tone (0-25)
    │     ├── Professional language register (+10)
    │     ├── Not inflammatory/clickbait (title + content) (+10)
    │     └── Consistent tone throughout (+5)
    │
    ├── Score attribution (0-25)
    │     ├── External links present (+10)
    │     ├── References section detected (+10)
    │     └── Inline citations or footnotes (+5)
    │
    ├── Composite score = structure + substance + tone + attribution
    │
    ├── Generate suggestions for improvement
    │     e.g. "Add a references section to improve attribution score (+10)"
    │
    ├── Set visibility tier:
    │     < 40 → noindex, hidden from search
    │     40-70 → indexed, searchable
    │     70+ → featured-eligible
    │
    └── Store score + breakdown in documents table
```

Scoring is deterministic (no LLM in the loop). Fast enough to run synchronously at publish time (< 100ms).

## Author Gravity Pipeline

```
Account verification event (domain confirmed / LinkedIn OAuth / ORCID linked)
    │
    ├── Recompute gravity_level:
    │     0 = email only
    │     1 = email + verified_domain
    │     2 = email + verified_domain + verified_linkedin
    │     3 = email + verified_domain + verified_linkedin + orcid_id
    │
    ├── Update accounts.gravity_level
    │
    ├── Emit gravity_updated event → Search index refresh
    │     (re-rank all documents by this author with new multiplier)
    │
    └── Notify author: "You've reached Level N — your documents now surface higher in search"

At publish time:
    ├── Snapshot current gravity_level into documents.author_gravity
    │     (immutable — reflects gravity the author had at publish)
    │
    └── Compute ranking_score = quality_score × gravity_multiplier
          Used by search API for result ordering
```

**Why snapshot gravity at publish time:** If an author earns ORCID after publishing 100 documents, those older documents should not retroactively gain maximum gravity. The gravity snapshot records the credibility the author had when they made the claim. Future documents benefit from higher gravity — incentivising continuous verification.

**Featured eligibility check:**
```python
gravity_thresholds = {0: 70, 1: 68, 2: 65, 3: 60}
is_featured_eligible = quality_score >= gravity_thresholds[author_gravity]
```

## Author Verification Pipeline

### Domain Verification

```
1. User: POST /v1/account/verify/domain  {domain: "example.com"}
2. Server: Returns TXT record to add: "lightpaper-verify=acct_xxx"
3. User: Adds DNS TXT record
4. User: GET /v1/account/verify/domain/check
5. Server: DNS lookup for TXT record → match → verified_domain = "example.com"
```

### LinkedIn Verification

```
1. User: GET /v1/account/verify/linkedin → redirect to LinkedIn OAuth
2. LinkedIn: User authorizes → callback with token
3. Server: Fetch profile, store verified_linkedin = true
```

### ORCID Verification

```
1. User: POST /v1/account/verify/orcid  {orcid: "0000-0002-1825-0097"}
2. Server: Verify ORCID iD exists via ORCID public API → store orcid_id
```

## Social Preview (Open Graph)

**OG image auto-generated** at publish time (Pillow), stored in Cloud Storage:

```
┌─────────────────────────────────────┐
│                                     │
│  lightpaper.org                     │
│                                     │
│  Straight Skeleton Algorithms       │
│  for Hip Roof Generation            │
│                                     │
│  A practical implementation guide   │
│  for steel frame construction       │
│                                     │
│  @jsmith · Feb 26, 2026         │
│  Quality: 78/100 · 15 min read      │
│                                     │
└─────────────────────────────────────┘
```

**1200 x 630px** — universal safe size for LinkedIn, Facebook, Twitter/X, WhatsApp, Slack, Discord, iMessage.

Monochrome design: `#FFFFFF` background, `#111827` text, Inter font. No colour accents. Clean and professional.

## CDN Strategy

**Cloud CDN + Cloud Load Balancing:**

- **Read path**: HTML cached at edge, `s-maxage=86400` (1 day). Purged on content update.
- **Write path**: `/v1/*` bypasses CDN (Cache-Control: no-store).
- **OG images**: Cached indefinitely in Cloud Storage, `s-maxage=31536000`. Regenerated on update.
- **Static discovery files**: `llms.txt`, `robots.txt`, `sitemap.xml` cached 1 hour.
- **Custom domains**: Google-managed SSL certificates via Cloud Load Balancing.

Cache purge on update:
```python
async def on_document_update(document):
    # Cloud CDN cache invalidation
    await cdn_client.invalidate_cache(
        url_map="your-cdn-url-map",
        path=f"/d/{document.id}",
    )
    await cdn_client.invalidate_cache(
        url_map="your-cdn-url-map",
        path=f"/{document.slug}",
    )
    # Regenerate OG image in Cloud Storage
    await generate_og_image(document)
```

## Spam Prevention (Agent-Compatible)

No CAPTCHAs. No anti-bot measures. Agents are first-class citizens.

**Layered defense:**

1. **Account verification** — Even free accounts require email verification (Firebase Auth). Creates accountability.
2. **Rate limiting** — Strict per-key limits via Memorystore Redis. Burst detection flags rapid publishing.
3. **Quality scoring** — Low-quality content is published but hidden (noindex, excluded from search). This is the primary defense against noise.
4. **Content scoring** — Lightweight classifier at publish time:
   - Text quality (entropy, repetition, coherence)
   - Known spam patterns (crypto scams, SEO farms)
   - Link density (high external link ratio = suspicious)
5. **Delayed indexing** — New accounts: documents published but `noindex` for 24 hours until reputation established.
6. **Reputation system** — Accounts accumulate reputation from: quality scores, view counts, content diversity, account age, zero abuse reports.
7. **Abuse reporting** — Every page has a subtle "Report" link. Confirmed abuse = account suspension.

## Performance Budget

| Metric | Target | How |
|--------|--------|-----|
| First Contentful Paint | < 500ms | SSR + inline CSS + Cloud CDN |
| Largest Contentful Paint | < 1.0s | No external CSS/JS blocking |
| Total page weight | < 50KB (text content) | Inline everything |
| JavaScript | < 5KB | Only: dark mode, progress bar, TOC scroll |
| Time to Interactive | < 500ms | Near-zero JS |
| CLS | 0 | font-display: swap + reserved image dimensions |

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cloud provider | Google Cloud | Best fit for async Python + managed PostgreSQL |
| App hosting | Cloud Run (Docker) | Serverless, auto-scaling, scale-to-zero |
| Database | Cloud SQL for PostgreSQL | Full-text search (tsvector + pg_trgm), JSONB, proven |
| Cache | Memorystore for Redis | Rate limits, idempotency, session cache |
| CDN | Cloud CDN + Cloud Load Balancing | Global edge, Google-managed SSL |
| Object storage | Cloud Storage | OG images, media uploads, content exports |
| Auth | Firebase Auth + API keys | Accounts for ownership, keys for API access |
| API style | REST | Simplest for agents |
| Content format | Markdown primary | LLMs produce Markdown natively |
| Rendering | Server-side (markdown-it-py + Pygments + KaTeX) | Zero client JS, perfect social previews |
| Design language | Monochrome (lightpaper aesthetic) | Content provides colour, chrome is invisible |
| Discovery | MCP + OpenAPI + A2A Agent Card + llms.txt (courtesy) | MCP for tool use, A2A for agent discovery, OpenAPI universal, llms.txt low-cost signal |
| Content negotiation | Accept header (HTML/JSON) | Same URL serves humans and agents |
| Semantic HTML | article/section/figure/figcaption | Four-audience readability |
| OG images | Pillow in Cloud Storage | Auto-generated at publish time |
| Search | PostgreSQL tsvector + pg_trgm | No external search service needed at launch |
| URL scheme | `/d/{id}` + `/{slug}` + `/@{handle}` + `/tag/{tag}` | Permanent ID + human-readable + author + tag |
| Quality scoring | Deterministic, no LLM | Fast (< 100ms), reproducible, transparent |
| Author gravity | Verification level (0-3) | Identity is evidence; snapshotted at publish |
| Authorship model | Human account always required | Accountability is the spam filter; no author_type complexity |
| Immutability | Versioned (not immutable) | Authors need to fix typos |
| Deletion | Soft delete → 410 Gone | URLs never reused |
| Spam prevention | Account reputation + quality scoring | No CAPTCHAs — agents are welcome |
