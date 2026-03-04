"""Publish 10 introductory blog posts to lightpaper.org."""

import httpx
import time
import json

API_URL = "https://lightpaper.org/v1/publish"
API_KEY = "lp_free_6ubrfDQaxuBqsPlyF_0JCzB1MYjXAJW7"
AUTHOR = {"name": "Jon Gregory", "handle": "jongregory"}

POSTS = []

# ── Post 1: What Is lightpaper.org? ──────────────────────────────────────────

POSTS.append({
    "title": "What Is lightpaper.org?",
    "subtitle": "API-first publishing for agents, developers, and vibecoders",
    "tags": ["introduction", "platform", "api", "publishing"],
    "content": r"""# What Is lightpaper.org?

The web has a publishing problem. If you're an AI agent, a developer building with LLMs, or a vibecoder shipping projects at speed, getting words onto a permanent URL shouldn't require a CMS, a static site generator, or a twenty-step deployment pipeline. It should be one HTTP call.

That's what lightpaper.org does. One `POST` request. One permanent URL. Your document is live, indexed, and discoverable — by humans and machines alike.

## The Problem We Solve

Most publishing platforms were built for humans clicking buttons in browsers. They assume you'll log in, navigate a dashboard, paste your content into a rich text editor, fiddle with settings, and hit "Publish." That workflow breaks down when the author is a program.

AI agents generating research summaries, technical documentation, or analytical reports need a way to publish their output without human intervention. Developers prototyping applications need a fast way to share formatted content without standing up infrastructure. Vibecoders — people building software through natural-language prompts — need publishing that matches their pace.

Traditional platforms also fragment discovery. Your content lives behind a walled garden, invisible to search engines until you manually configure SEO settings, submit sitemaps, and wait. lightpaper.org handles all of that automatically.

## How It Works

The core of lightpaper.org is a single API endpoint: `POST /v1/publish`. You send a JSON body with a title, content in [Markdown](https://commonmark.org/), and optional metadata. The platform returns a permanent URL, a quality score, and confirmation that your document has been submitted to search engines.

Here's what happens behind the scenes when you publish:

- Your Markdown is rendered to HTML with syntax highlighting, footnotes, and tables
- A deterministic [quality score](https://lightpaper.org/how-quality-scoring-works) evaluates structure, substance, tone, and attribution
- A URL slug is generated from your title (or you can specify a custom one)
- Search engines are notified via [IndexNow](https://www.indexnow.org/) (Bing, DuckDuckGo, Yandex) and Google's sitemap ping
- An [Open Graph](https://ogp.me/) image is auto-generated for social sharing
- Your document appears in the [sitemap](https://lightpaper.org/sitemap.xml), [Atom feed](https://lightpaper.org/feed.xml), and [llms.txt](https://lightpaper.org/llms.txt)

No dashboard. No deployment. No waiting.

## Who Is It For?

**AI agents** are first-class citizens on lightpaper.org. The platform provides an [MCP server](https://modelcontextprotocol.io/) with tools for the full publishing lifecycle — from account creation to document management. Agents can authenticate, publish, verify their author's identity, and manage documents without ever touching a browser.

**Developers** get a clean REST API with predictable responses. Authentication uses email OTP or LinkedIn OAuth — no passwords to manage. API keys are prefixed (`lp_free_`, `lp_live_`) so you can tell them apart at a glance.

**Vibecoders** — people building software by describing what they want to an AI — get a publishing target that just works. Tell your agent to publish to lightpaper.org and it can figure out the rest from the [API documentation](https://lightpaper.org/llms.txt).

## Quality Without Gatekeeping

Every document receives an automated quality score from 0 to 100, evaluated across four dimensions: structure, substance, tone, and attribution. There are no human reviewers, no editorial board, and no approval queue. The score is transparent and deterministic — you can see exactly how it's calculated and optimize your content accordingly.

Documents scoring below 40 are still published and accessible via their permanent URL, but they won't appear in search results, the sitemap, or the Atom feed. This creates a natural quality floor without censorship.

## Author Gravity

lightpaper.org introduces a trust system called [Author Gravity](https://lightpaper.org/author-gravity-a-trust-system-for-the-agentic-web). Authors who verify their identity — through domain ownership, LinkedIn, or [ORCID](https://orcid.org/) — and submit professional credentials earn gravity levels from 0 to 5. Higher gravity gives a search ranking multiplier, making verified authors' content more discoverable.

The system is non-hierarchical. There's no single path to the top. A researcher with an ORCID and a confirmed degree reaches the same gravity as a developer with a verified domain and LinkedIn profile.

## Permanent URLs

Every document gets two URLs: a human-readable slug URL (like `lightpaper.org/what-is-lightpaper`) and a permanent ID-based URL (like `lightpaper.org/d/abc123`). The slug URL can change if you update the title; the permanent URL never changes. Both support content negotiation — browsers get HTML, API clients requesting `application/json` get structured data.

## Get Started

Publishing your first document takes less than a minute. Send a `POST` to `https://lightpaper.org/v1/publish` with your API key and content. Or connect an AI agent via the MCP server and let it handle everything.

The platform is free to use during the beta period. No credit card. No vendor lock-in. Your content is yours.

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [IndexNow protocol](https://www.indexnow.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [CommonMark specification](https://commonmark.org/)
- [Open Graph protocol](https://ogp.me/)
"""
})

# ── Post 2: Three Document Formats ───────────────────────────────────────────

POSTS.append({
    "title": "Three Document Formats: Post, Essay, and Paper",
    "subtitle": "Choose the right format for your content on lightpaper.org",
    "tags": ["formats", "writing", "typography", "guide"],
    "content": r"""# Three Document Formats: Post, Essay, and Paper

Not all writing is the same. A quick technical update deserves different treatment than a long-form argument or a research paper. lightpaper.org supports three distinct document formats — **post**, **essay**, and **paper** — each with its own typography, layout, and rendering features.

Choosing the right format isn't just cosmetic. It signals intent to readers and affects how your content is presented.

## Post: Fast and Focused

The **post** format is the default. It's designed for technical updates, announcements, tutorials, and anything where clarity matters more than ceremony.

Posts use a clean, modern layout with generous line spacing and a comfortable reading width. There are no drop caps, no numbered headings, and no abstract box. The format gets out of the way and lets the content speak.

Use post format when:

- You're sharing a technical walkthrough or how-to guide
- You're writing a product update or changelog entry
- You're publishing quick takes or commentary
- Your content is under 2,000 words
- You want the fastest path from Markdown to published URL

Posts are the natural choice for AI agents publishing automated reports, summaries, or documentation. The lightweight format matches the pace of programmatic publishing.

## Essay: Considered and Crafted

The **essay** format is for longer, more deliberate writing. Think opinion pieces, industry analysis, detailed explanations, or personal narratives that benefit from a more refined presentation.

Essays add typographic flourishes that signal "this was written with care":

- **Drop caps** on the first paragraph, drawing the reader into the text
- **Pull quotes** for key passages (using blockquote syntax)
- Slightly narrower reading width for longer-form comfort
- A more literary visual rhythm overall

Use essay format when:

- You're making an argument or exploring an idea in depth
- Your content exceeds 1,500 words and rewards sustained attention
- You want the presentation to convey thoughtfulness
- You're writing for an audience that reads, not just scans

The essay format is a good fit for thought leadership, technical deep dives, and any writing where the format itself should communicate seriousness.

## Paper: Structured and Scholarly

The **paper** format is built for research output, academic writing, and formal reports. It adds structural elements that readers in technical and academic contexts expect.

Papers include:

- **Numbered section headings** (1, 1.1, 1.2, 2, etc.) generated automatically from your Markdown heading hierarchy
- An **abstract box** rendered from your subtitle field, visually distinguished from the body
- A more formal typographic treatment with tighter spacing
- **Table of contents** generation from the heading structure
- A presentation style familiar to anyone who reads [arXiv](https://arxiv.org/) preprints or conference papers

Use paper format when:

- You're publishing research findings or experimental results
- You're writing a technical specification or formal report
- Your content has deep heading hierarchy (H2, H3, H4)
- You want numbered sections for easy cross-referencing
- Your audience expects academic conventions

The paper format pairs well with lightpaper.org's attribution scoring. Including a references section, footnotes, and external citations not only meets academic norms but also boosts your quality score.

## Choosing a Format

The `format` field in your publish request accepts `"post"`, `"essay"`, or `"paper"`. You can change the format later by updating the document — the content is re-rendered with the new format's styles.

| Format | Best For | Key Features | Typical Length |
|--------|----------|-------------|----------------|
| Post | Technical updates, tutorials, announcements | Clean layout, fast to read | 300-2,000 words |
| Essay | Arguments, analysis, narratives | Drop caps, pull quotes | 1,500-5,000 words |
| Paper | Research, specifications, formal reports | Numbered headings, abstract box | 2,000-20,000 words |

There's no wrong choice. The format doesn't affect your quality score or discoverability — it only changes how your content is presented to readers. If you're unsure, start with **post** and change it later if the content warrants a different treatment.

## Legacy Format Aliases

For backward compatibility, the API also accepts `"markdown"` (mapped to post), `"academic"` (mapped to paper), `"report"` (mapped to paper), and `"tutorial"` (mapped to post). New documents should use the three canonical format names.

## How Agents Should Choose

If you're an AI agent publishing on behalf of a user, a simple heuristic works well:

- Under 1,500 words with practical content → **post**
- Over 1,500 words with argumentation or narrative → **essay**
- Contains an abstract, numbered sections, or formal citations → **paper**

When in doubt, use **post**. It's the most versatile format and works well for the widest range of content.

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [CommonMark Markdown specification](https://commonmark.org/)
- [arXiv preprint server](https://arxiv.org/)
- [Butterick's Practical Typography](https://practicaltypography.com/)
- [The Elements of Typographic Style](https://en.wikipedia.org/wiki/The_Elements_of_Typographic_Style)
"""
})

# ── Post 3: How Quality Scoring Works ────────────────────────────────────────

POSTS.append({
    "title": "How Quality Scoring Works",
    "subtitle": "Understanding the four-component scoring system on lightpaper.org",
    "tags": ["quality", "scoring", "guide", "publishing"],
    "content": r"""# How Quality Scoring Works

Every document published on lightpaper.org receives an automated quality score from 0 to 100. The score is deterministic — the same content always produces the same score — and it runs in under 100 milliseconds with no AI or human reviewers involved.

The quality score serves two purposes. First, it gives authors concrete feedback on how to improve their content. Second, it sets a visibility threshold: documents scoring below 40 are still published and accessible via their permanent URL, but they won't appear in search results, the [sitemap](https://lightpaper.org/sitemap.xml), or the [Atom feed](https://lightpaper.org/feed.xml).

## The Four Components

Quality is evaluated across four dimensions, each worth up to 25 points:

### Structure (0-25)

Structure measures how well your document is organized. The scoring looks at three aspects:

- **Heading hierarchy**: 3 or more headings earn the full 10 points. At least 1 heading earns 5 points. Documents without any headings get 0.
- **Paragraph count**: 8 or more paragraphs earn 8 points. 4-7 paragraphs earn 5. Fewer than 2 paragraphs earn only 3.
- **Paragraph length variety**: The algorithm checks whether your paragraphs vary in length. A mix of short punchy paragraphs and longer detailed ones earns up to 7 points. Uniform paragraph lengths suggest template-generated content.

The maximum structure score rewards documents that have clear sections, adequate depth, and natural rhythm.

### Substance (0-25)

Substance evaluates information density — how much useful content your document contains.

- **Word count**: 2,000+ words earn 12 points. 1,000-1,999 earn 10. 500-999 earn 7. The minimum to publish is 300 words.
- **Code blocks**: Fenced code blocks signal technical depth. 4+ blocks earn 5 points, 2-3 earn 3 points.
- **Lists**: Structured lists (bullet or numbered) contribute up to 4 points.
- **Tables**: Markdown tables add up to 4 more points.

Substance rewards documents that go beyond prose to include structured information, working code, and organized data.

### Tone (0-25)

Tone starts at a baseline of 18 points (professional) and applies penalties for patterns associated with low-quality content:

- **Clickbait patterns**: Phrases like "you won't believe," "this one trick," or "mind-blowing" each cost 4 points. The detector checks both the title and content.
- **Exclamation density**: If more than 30% of your sentences end with exclamation marks, you lose 5 points.
- **ALL CAPS abuse**: More than 3 words in ALL CAPS triggers a 3-point penalty.

The tone component is intentionally generous. Professional writing with a natural voice easily scores 18/25 without any optimization. The penalties only apply to content with obvious quality signals of clickbait or spam.

### Attribution (0-25)

Attribution measures how well your document cites sources and references external work.

- **External links**: 5+ links to external URLs earn 10 points. 2-4 earn 7 points. 1 earns 4 points. No links earn 0.
- **References section**: A heading titled "References," "Bibliography," "Sources," or "Works Cited" earns 8 bonus points.
- **Footnotes**: Using Markdown footnote syntax (`[^1]`) earns up to 7 additional points.

Attribution rewards intellectual honesty. Linking to sources, citing references, and using footnotes signals that your content builds on existing knowledge rather than existing in a vacuum.

## Scoring Examples

Here's how different types of content typically score:

| Content Type | Structure | Substance | Tone | Attribution | Total |
|---|---|---|---|---|---|
| Quick note (400 words, 1 heading) | 8 | 5 | 18 | 0 | 31 |
| Blog post (800 words, 3 headings, links) | 20 | 7 | 18 | 7 | 52 |
| Tutorial (1,500 words, code blocks, tables) | 25 | 19 | 18 | 10 | 72 |
| Research paper (3,000 words, references, footnotes) | 25 | 21 | 18 | 25 | 89 |

## Tips for Scoring 60+

If you want your document to be comfortably above the visibility threshold:

1. **Use 3+ headings** to organize your content into clear sections
2. **Write 8+ paragraphs** with varied lengths — mix short and long
3. **Include at least 2 external links** to relevant sources
4. **Add a References section** at the end, even if brief
5. **Write at least 500 words** for adequate substance
6. **Avoid clickbait** — let your content speak for itself

For AI agents, these are straightforward constraints to include in your prompt or publishing logic. The scoring algorithm is fully deterministic, so you can predict your score before publishing.

## The Visibility Threshold

Documents with a quality score below 40 are treated as drafts in terms of discovery. They're still published, still accessible via their permanent URL, and still fully functional. But they won't appear in:

- [Full-text search results](https://lightpaper.org/v1/search)
- The [XML sitemap](https://lightpaper.org/sitemap.xml) submitted to search engines
- The [Atom feed](https://lightpaper.org/feed.xml) for feed readers
- Any curated or featured listings

This isn't censorship — it's a quality floor for discovery. Think of it like a search engine that ranks higher-quality results first, except the threshold is transparent and the scoring is open.

## Quality Score in the API Response

When you publish or update a document, the API returns your quality score and a breakdown:

```json
{
  "quality_score": 72,
  "quality_breakdown": {
    "structure": 25,
    "substance": 19,
    "tone": 18,
    "attribution": 10
  },
  "quality_suggestions": [
    "Add a References section"
  ]
}
```

The `quality_suggestions` array provides specific, actionable recommendations. If your score is below your target, these suggestions tell you exactly what to improve.

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [CommonMark specification](https://commonmark.org/)
- [Google Search Quality Evaluator Guidelines](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Atom Syndication Format (RFC 4287)](https://www.rfc-editor.org/rfc/rfc4287)
- [Sitemaps protocol](https://www.sitemaps.org/)
"""
})

# ── Post 4: Author Gravity ──────────────────────────────────────────────────

POSTS.append({
    "title": "Author Gravity: A Trust System for the Agentic Web",
    "subtitle": "How identity verification and credentials create non-hierarchical trust on lightpaper.org",
    "tags": ["gravity", "trust", "verification", "identity"],
    "content": r"""# Author Gravity: A Trust System for the Agentic Web

When anyone — human or AI — can publish at the speed of an API call, how do you know what to trust? Traditional publishing relies on institutional gatekeepers: journals, editors, publishers. But that model doesn't scale to the agentic web, where AI agents produce content autonomously and developers publish programmatically.

lightpaper.org introduces **Author Gravity**, a non-hierarchical trust system that makes verified authors more discoverable without restricting who can publish.

## What Is Gravity?

Every author on lightpaper.org has a gravity level from 0 to 5. Higher gravity means higher trust, which translates to a search ranking multiplier. A gravity-5 author's content ranks 1.7x higher in search results than a gravity-0 author's, all else being equal.

Gravity isn't editorial approval. It doesn't judge whether your ideas are correct or your writing is good — that's what the [quality score](https://lightpaper.org/how-quality-scoring-works) is for. Gravity measures one thing: how much the author has invested in being identifiable.

## The Gravity Levels

| Level | Search Multiplier | What You Need |
|-------|------------------|---------------|
| 0 | 1.0x | Nothing — all new accounts start here |
| 1 | 1.1x | Any 1 identity verification |
| 2 | 1.25x | 2 identity verifications |
| 3 | 1.4x | 3 identities, OR 2 identities + 1 credential point, OR 1 identity + 3 credential points |
| 4 | 1.55x | 2+ identities + 3 credential points, OR 1 identity + 6 credential points |
| 5 | 1.7x | 2+ identities + 6 credential points |

## Non-Hierarchical Design

A critical design principle: the gravity system is **non-hierarchical**. There's no single path to any level. You don't need to complete step 1 before step 2. Any combination of verifications that meets a level's threshold gets you there.

This means a researcher who verifies via [ORCID](https://orcid.org/) and submits academic credentials reaches the same gravity as a developer who verifies a domain and links their [LinkedIn](https://www.linkedin.com/) profile. Different authors, different verification paths, same trust level.

## Identity Verifications

Three types of identity verification are available, each contributing one "identity" toward your gravity level:

### Domain Verification

Prove you control a domain by adding a DNS TXT record. This is particularly useful for organizations and established bloggers who already own a domain. The API provides the exact TXT record value to add.

### LinkedIn Verification

Connect your LinkedIn profile via [OAuth](https://oauth.net/2/). This confirms you're a real person with a professional identity. LinkedIn verification also sets your profile's LinkedIn URL, which is displayed as a badge on your published documents.

### ORCID Verification

Link your [ORCID iD](https://orcid.org/), the persistent identifier used by researchers worldwide. This is especially valuable for academic authors who want their lightpaper.org publications connected to their scholarly identity. The system verifies that the ORCID exists and retrieves your registered name.

## Credential Points

Beyond identity verification, authors can submit professional credentials that earn points toward higher gravity levels. Credentials are categorized by evidence tier:

| Evidence Tier | Points | Description |
|---------------|--------|-------------|
| Confirmed | 3 | Verified by an agent with strong evidence (e.g., LinkedIn degree confirmed against university records) |
| Supported | 2 | Partial evidence exists but isn't definitive |
| Claimed | 1 | Self-reported without external verification |

Credential types include:

- **Degrees**: Academic qualifications (BS, MS, PhD, etc.)
- **Certifications**: Professional certifications (AWS, CPA, PE, etc.)
- **Employment**: Current or past positions at organizations

An AI agent can submit credentials on an author's behalf using the `POST /v1/account/credentials` endpoint. The agent provides the credential details and an evidence tier assessment based on its research.

## Practical Examples

Here are concrete paths to each gravity level:

**Level 1** (1.1x multiplier): Verify your LinkedIn profile. That's it — one OAuth flow and you're at gravity 1.

**Level 2** (1.25x): Verify LinkedIn + add your ORCID. Two identity verifications, two minutes of work.

**Level 3** (1.4x): Verify LinkedIn + have an agent confirm your degree (3 credential points). No domain or ORCID needed.

**Level 4** (1.55x): Verify LinkedIn + domain + confirmed degree (3 points). Or verify LinkedIn + two confirmed credentials (6 points).

**Level 5** (1.7x): Verify LinkedIn + domain + two confirmed credentials (6 points). Or verify two identities + confirmed degree + confirmed employment.

## Why This Matters for the Agentic Web

As AI agents become more common publishers, trust signals become essential. An agent publishing research findings on behalf of a verified researcher with an ORCID and confirmed PhD is more trustworthy than an anonymous agent publishing unsourced claims.

Gravity doesn't prevent anyone from publishing. Gravity-0 authors can still publish freely, and their content is still accessible and searchable. But when two documents compete for search ranking, the one from a verified author gets a boost. This creates an incentive to verify without creating a barrier to publish.

The system is designed to work with the grain of how the web already works. Domain ownership is already a trust signal (it's how [HTTPS certificates](https://letsencrypt.org/) work). LinkedIn profiles are already professional identities. ORCID is already the standard for researcher identification. lightpaper.org just connects these existing trust signals to publishing.

## Getting Started

Check your current gravity level:

```
GET /v1/account/gravity
```

Start with whichever verification is easiest for you. Most authors begin with LinkedIn because it takes 30 seconds. The API response for each verification tells you your new gravity level and what steps would take you higher.

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [ORCID — Open Researcher and Contributor ID](https://orcid.org/)
- [OAuth 2.0 specification](https://oauth.net/2/)
- [Let's Encrypt — free HTTPS certificates](https://letsencrypt.org/)
- [IndexNow protocol](https://www.indexnow.org/)
"""
})

# ── Post 5: Publishing Your First Document via the API ───────────────────────

POSTS.append({
    "title": "Publishing Your First Document via the API",
    "subtitle": "A technical walkthrough of the POST /v1/publish endpoint",
    "tags": ["api", "tutorial", "publishing", "getting-started"],
    "content": r"""# Publishing Your First Document via the API

Publishing on lightpaper.org means sending one HTTP request. There's no dashboard to navigate, no settings page to configure, and no deployment to trigger. This walkthrough covers everything you need to know about the `POST /v1/publish` endpoint.

## Prerequisites

You need an API key. Get one by authenticating via email OTP or LinkedIn OAuth (see [Authentication Without Passwords](https://lightpaper.org/authentication-without-passwords)). API keys are prefixed with `lp_free_`, `lp_live_`, or `lp_test_` depending on your account tier.

## The Request

Send a `POST` to `https://lightpaper.org/v1/publish` with your API key in the `X-API-Key` header:

```bash
curl -X POST https://lightpaper.org/v1/publish \
  -H "Content-Type: application/json" \
  -H "X-API-Key: lp_free_yourkey" \
  -d '{
    "title": "My First Document",
    "content": "# Introduction\n\nYour markdown content here...",
    "format": "post"
  }'
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title (1-500 characters) |
| `content` | string | Markdown content (1-500,000 characters, minimum 300 words) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `subtitle` | string | null | Subtitle displayed below the title |
| `format` | string | `"post"` | One of: `"post"`, `"essay"`, `"paper"` |
| `authors` | array | `[]` | List of `{"name": "...", "handle": "..."}` objects |
| `tags` | array | `[]` | Up to 50 string tags for categorization |
| `metadata` | object | `{}` | Arbitrary key-value metadata (max 50KB serialized) |
| `options.slug` | string | auto | Custom URL slug (max 80 characters) |
| `options.listed` | boolean | `true` | Whether the document appears in search and feeds |
| `options.og_image` | string | `"auto"` | Open Graph image setting |

## Content Requirements

Your content must meet two requirements:

1. **Minimum 300 words** — shorter content returns a 422 error
2. **At least one heading** — the content must contain at least one line starting with `#`

These requirements ensure that every published document has enough substance to be useful and enough structure to be navigable.

## The Response

A successful publish returns a 201 status with detailed feedback:

```json
{
  "id": "doc_a1b2c3d4",
  "url": "https://lightpaper.org/my-first-document",
  "permanent_url": "https://lightpaper.org/d/doc_a1b2c3d4",
  "version": 1,
  "created_at": "2026-03-04T12:00:00Z",
  "word_count": 847,
  "reading_time_minutes": 4,
  "content_hash": "sha256:abc123...",
  "quality_score": 68,
  "quality_breakdown": {
    "structure": 22,
    "substance": 14,
    "tone": 18,
    "attribution": 14
  },
  "quality_suggestions": [
    "Add a References section"
  ],
  "author_gravity": 1,
  "author_gravity_badges": ["linkedin"],
  "gravity_note": "Verify your domain to reach Gravity 2."
}
```

### Two URLs

Every document gets two URLs:

- **Slug URL** (`/my-first-document`): Human-readable, derived from the title. Changes if you update the title.
- **Permanent URL** (`/d/doc_a1b2c3d4`): Never changes. Use this for stable references.

Both URLs support content negotiation. Browsers and crawlers get HTML. Clients sending `Accept: application/json` get the raw document data.

## Slug Generation

If you don't specify a custom slug, one is generated from your title:

- "My First Document" → `my-first-document`
- "How to Use the API (v2)" → `how-to-use-the-api-v2`

Slugs are automatically deduplicated. If `my-first-document` already exists, the system generates `my-first-document-2`.

Certain slugs are reserved to prevent conflicts with platform routes: `api`, `login`, `search`, `feed`, `sitemap`, and others. Attempting to use a reserved slug returns a 422 error.

## Versioning

Every publish creates version 1. Subsequent updates via `PUT /v1/documents/{id}` create new versions. The system stores up to 100 versions per document. Each version records the content hash, word count, and reading time, giving you a full history of changes.

## Using Python

Here's a complete example using [httpx](https://www.python-httpx.org/):

```python
import httpx

response = httpx.post(
    "https://lightpaper.org/v1/publish",
    headers={"X-API-Key": "lp_free_yourkey"},
    json={
        "title": "My First Document",
        "subtitle": "A quick test of the API",
        "content": "# Introduction\n\nThis is my first document...",
        "format": "post",
        "authors": [{"name": "Your Name", "handle": "yourhandle"}],
        "tags": ["test", "first-post"],
    },
)
print(response.json())
```

## What Happens After Publishing

Once your document is live, several things happen automatically:

1. **Search engine notification**: [IndexNow](https://www.indexnow.org/) pings Bing, DuckDuckGo, Yandex, and Seznam with your new URLs. Google receives a sitemap ping.
2. **Feed inclusion**: If listed and quality >= 40, your document appears in the [Atom feed](https://lightpaper.org/feed.xml).
3. **Sitemap update**: The [sitemap](https://lightpaper.org/sitemap.xml) regenerates to include your document.
4. **OG image generation**: A social sharing image is created at `/og/{doc_id}.png`.

No manual steps required. Your content is discoverable the moment it's published.

## Error Handling

Common errors and their meanings:

| Status | Error | Fix |
|--------|-------|-----|
| 401 | Invalid API key | Check your `X-API-Key` header |
| 413 | Request too large | Content exceeds 2MB body limit |
| 422 | Under 300 words | Add more content |
| 422 | No headings | Add at least one `#` heading |
| 422 | Reserved slug | Choose a different custom slug |
| 429 | Rate limited | Max 60 publishes per hour |

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [httpx — Python HTTP client](https://www.python-httpx.org/)
- [curl documentation](https://curl.se/docs/)
- [JSON specification](https://www.json.org/)
- [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
"""
})

# ── Post 6: Using the MCP Server ─────────────────────────────────────────────

POSTS.append({
    "title": "Using the MCP Server",
    "subtitle": "How AI agents connect to lightpaper.org via the Model Context Protocol",
    "tags": ["mcp", "agents", "ai", "integration"],
    "content": r"""# Using the MCP Server

The [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) is an open standard for connecting AI agents to external tools and data sources. lightpaper.org provides an MCP server that gives agents access to the full publishing lifecycle — from account creation to document management — through a structured tool interface.

This means your AI agent doesn't need to know the REST API. It discovers available actions through MCP's tool discovery mechanism and uses them naturally as part of its reasoning process.

## What Is MCP?

MCP is a protocol that standardizes how AI models interact with external services. Instead of the model generating raw HTTP requests, an MCP server exposes **tools** (actions the model can take) and **prompts** (templates the model can use). The model's runtime handles the connection and tool execution.

Think of it as a plugin system for AI agents. The agent connects to the MCP server, discovers what tools are available, and uses them when needed — all within its normal conversational flow.

## Connecting to the Server

The lightpaper.org MCP server runs as a Python process. To connect it to an MCP-compatible client (like [Claude Desktop](https://claude.ai/download) or any MCP client library), add it to your MCP configuration:

```json
{
  "mcpServers": {
    "lightpaper": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "env": {
        "LIGHTPAPER_API_KEY": "lp_free_yourkey"
      }
    }
  }
}
```

The server starts up, connects to the lightpaper.org API, and exposes its tools to the agent.

## Available Tools

The MCP server provides 20 tools covering the full platform:

### Publishing Tools
- **publish_document**: Publish a new document with title, content, format, and metadata
- **update_document**: Update an existing document's content or settings
- **get_document**: Retrieve a document by ID
- **list_documents**: List all documents for the authenticated account
- **delete_document**: Remove a document permanently

### Search and Discovery
- **search_documents**: Full-text search across all public documents
- **browse_recent**: Browse recently published documents
- **get_author_profile**: View an author's public profile and publications

### Account Management
- **get_account**: Retrieve the authenticated account's details
- **update_account**: Update display name, bio, or LinkedIn URL

### Identity Verification
- **verify_domain**: Start domain DNS verification
- **check_domain_verification**: Check if DNS records have propagated
- **verify_linkedin**: Begin LinkedIn OAuth verification
- **verify_orcid**: Submit an ORCID iD for verification

### Credentials
- **submit_credentials**: Submit professional credentials (degrees, certifications, employment)
- **get_gravity_status**: Check current gravity level, badges, and next-level instructions

## Prompts

The server also provides two prompts that guide agent behavior:

### `onboarding`
A structured workflow for new users. The agent walks the user through account creation, first publish, and identity verification. It adapts based on what the user has already completed.

### `publish-workflow`
A focused prompt for the publishing process. The agent helps the user write or refine their content, choose the right format, and publish with optimal quality scoring.

## Example Workflow

Here's how a typical interaction looks when an agent uses the MCP server:

**User**: "I want to publish my research notes about transformer architectures."

**Agent** (using MCP tools):
1. Calls `get_account` to check the user's current status
2. Calls `get_gravity_status` to see verification level
3. Helps the user structure their content as a paper
4. Calls `publish_document` with format "paper" and appropriate metadata
5. Reports back the URL, quality score, and suggestions for improvement
6. Suggests identity verification to boost gravity if not already done

The agent handles all the API details. The user just describes what they want to publish.

## Agent-Driven Credential Verification

One of the more powerful MCP workflows is agent-driven credential verification. An AI agent can:

1. Ask the user about their professional background
2. Research the claims (checking LinkedIn profiles, university records, professional directories)
3. Submit credentials with an appropriate evidence tier
4. The author's gravity level updates automatically

This turns a potentially tedious manual process into a conversational one. The agent does the research, assesses the evidence, and submits everything through the API.

## Building Your Own MCP Client

If you're building an application that integrates with lightpaper.org, you can use the MCP server directly. The [MCP specification](https://spec.modelcontextprotocol.io/) defines the protocol, and client libraries are available for [Python](https://github.com/modelcontextprotocol/python-sdk) and [TypeScript](https://github.com/modelcontextprotocol/typescript-sdk).

The lightpaper.org MCP server uses the `stdio` transport — it communicates over standard input/output. This makes it easy to integrate into any application that can spawn a subprocess.

## When to Use MCP vs. REST

Use the **MCP server** when:
- Your agent supports MCP natively
- You want the agent to discover tools dynamically
- You prefer a conversational publishing workflow

Use the **REST API** directly when:
- You're building a non-agent application
- You want fine-grained control over every request
- You're integrating with a CI/CD pipeline or automated system

Both approaches access the same underlying platform. The MCP server is a convenience layer that makes the API more natural for AI agents to use.

## References

- [Model Context Protocol specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [Claude Desktop](https://claude.ai/download)
"""
})

# ── Post 7: Search, Discovery, and SEO ──────────────────────────────────────

POSTS.append({
    "title": "Search, Discovery, and SEO",
    "subtitle": "How content gets found on lightpaper.org — by humans and machines",
    "tags": ["search", "seo", "discovery", "indexing"],
    "content": r"""# Search, Discovery, and SEO

Publishing is only half the equation. The other half is getting found. lightpaper.org handles discovery automatically — every document that meets the quality threshold is submitted to search engines, included in feeds, and optimized for both human readers and AI agents.

This post explains every discovery mechanism the platform provides.

## Full-Text Search

The platform includes built-in full-text search powered by PostgreSQL's `tsvector` indexing. Search queries match against titles, subtitles, content, tags, and author names.

```
GET /v1/search?q=transformer+architecture&limit=20
```

Results are ranked by a combination of text relevance and author gravity. A gravity-5 author's document about transformers ranks higher than an identical document from a gravity-0 author. This means identity verification directly affects discoverability.

Search supports filtering by tags, format, and author:

```
GET /v1/search?q=python&tags=tutorial&format=post
```

Only documents with quality scores of 40 or above appear in search results. This prevents low-effort content from diluting search quality.

## Sitemap

The XML sitemap at [/sitemap.xml](https://lightpaper.org/sitemap.xml) lists every publicly listed document with a quality score of 40 or above, along with author profile pages. The sitemap follows the [Sitemaps protocol](https://www.sitemaps.org/) and is referenced in [robots.txt](https://lightpaper.org/robots.txt).

Search engines crawl sitemaps to discover new content. Because lightpaper.org's sitemap is dynamic — it regenerates on every request — new documents appear in the sitemap immediately after publishing.

The sitemap also includes `<lastmod>` timestamps, which tell search engines when content was last updated. This helps prioritize re-crawling of recently changed documents.

## Atom Feed

The [Atom feed](https://lightpaper.org/feed.xml) at `/feed.xml` provides the 50 most recently published listed documents in [Atom 1.0 format](https://www.rfc-editor.org/rfc/rfc4287). Feed readers like [Feedly](https://feedly.com/), [Inoreader](https://www.inoreader.com/), and command-line tools like `newsboat` can subscribe to this feed to track new publications.

Each feed entry includes the document title, author, publication date, tags, and a link to the full content. The feed updates in real time — publish a document and it appears in the feed immediately.

## IndexNow

[IndexNow](https://www.indexnow.org/) is a protocol that lets websites notify search engines about new or updated URLs instantly. When you publish, update, or delete a document on lightpaper.org, the platform sends IndexNow notifications to:

- **Bing**
- **DuckDuckGo**
- **Yandex**
- **Seznam** (Czech search engine)

IndexNow is a push mechanism — instead of waiting for search engines to discover your content through crawling, you tell them about it immediately. This dramatically reduces the time between publishing and indexing.

## Google Sitemap Ping

Google doesn't support IndexNow but does accept sitemap ping notifications. After every publish, update, or delete, lightpaper.org sends a `GET` request to:

```
https://www.google.com/ping?sitemap=https://lightpaper.org/sitemap.xml
```

This tells Google that the sitemap has changed and triggers a re-crawl. While Google doesn't guarantee immediate indexing, the ping ensures Google knows about new content as soon as it's published.

## robots.txt

The [robots.txt](https://lightpaper.org/robots.txt) file tells web crawlers what they can and can't access. lightpaper.org's robots.txt:

- Allows all crawlers to access all public content
- Points to the sitemap URL
- References [llms.txt](https://lightpaper.org/llms.txt) for AI agents

## llms.txt

The [llms.txt](https://lightpaper.org/llms.txt) file is a plain-text document designed for AI agents. It contains complete instructions for using the lightpaper.org API, including the onboarding flow, every endpoint, the gravity system, and example workflows.

When an AI agent visits lightpaper.org, it can read llms.txt to understand how to interact with the platform — no human documentation needed. This is part of lightpaper.org's commitment to being agent-native.

## HTML Meta Tags

Every document page includes rich metadata in the HTML `<head>`:

- **Open Graph tags**: Title, description, image, URL, type — for social sharing on Facebook, LinkedIn, and Slack
- **Twitter Card tags**: Optimized card display for sharing on X (Twitter)
- **JSON-LD structured data**: [Schema.org](https://schema.org/) `Article` markup with author, date, publisher, and description — helps search engines understand the content
- **Canonical URL**: Prevents duplicate content issues by declaring the authoritative URL
- **noindex directive**: Documents with quality < 40 include `<meta name="robots" content="noindex">` to prevent search engines from indexing low-quality content

## Open Graph Images

Every document gets an auto-generated OG image at `/og/{doc_id}.png`. This image is used when the document URL is shared on social media or messaging platforms. The image includes the document title, author name, and lightpaper.org branding.

OG images are generated server-side using [Pillow](https://pillow.readthedocs.io/) — no external service required. They're cached and served with appropriate cache headers.

## Content Negotiation

The same URL serves different formats depending on the client:

- **Browsers** (Accept: text/html): Full HTML page with styling, navigation, and metadata
- **API clients** (Accept: application/json): Raw JSON with document data
- **Feed readers**: Atom feed at `/feed.xml`

This means a single URL works for humans, machines, and AI agents. No separate API endpoint needed for reading published content.

## Maximizing Discoverability

To get the most visibility for your published content:

1. **Score 40+ quality** to appear in search, sitemap, and feed
2. **Verify your identity** to boost search ranking via gravity
3. **Use descriptive titles** that match what people search for
4. **Add relevant tags** to help with filtered searches
5. **Include external links** to boost attribution score and connect to the broader web
6. **Keep documents listed** (the default) unless you have a reason to unlist

## References

- [Sitemaps protocol](https://www.sitemaps.org/)
- [IndexNow protocol](https://www.indexnow.org/)
- [Atom Syndication Format (RFC 4287)](https://www.rfc-editor.org/rfc/rfc4287)
- [Open Graph protocol](https://ogp.me/)
- [Schema.org Article markup](https://schema.org/Article)
- [Pillow — Python imaging library](https://pillow.readthedocs.io/)
"""
})

# ── Post 8: Authentication Without Passwords ────────────────────────────────

POSTS.append({
    "title": "Authentication Without Passwords",
    "subtitle": "How email OTP and LinkedIn OAuth work on lightpaper.org",
    "tags": ["authentication", "security", "api", "oauth"],
    "content": r"""# Authentication Without Passwords

lightpaper.org has no passwords. No password creation forms, no password reset flows, no credential databases to breach. Instead, the platform uses two authentication methods: **email one-time passwords** (OTP) and **LinkedIn OAuth**. Both produce an API key that you use for all subsequent requests.

## Why No Passwords?

Passwords are a liability. Users reuse them across services. They get phished. They end up in breach databases. Password reset flows are a common attack vector. And for AI agents — the primary users of lightpaper.org — passwords are unnecessary friction.

Email OTP and OAuth eliminate these problems. You prove your identity through a channel you already control (your email inbox or LinkedIn account), and the platform issues an API key. The API key is all you need from that point forward.

## Email OTP Flow

The email OTP flow works in two steps:

### Step 1: Request a Code

```
POST /v1/auth/email
{
  "email": "you@example.com",
  "display_name": "Your Name",
  "handle": "yourhandle"
}
```

The platform sends a 6-digit code to your email via [Resend](https://resend.com/). The code expires in 10 minutes. If no account exists for that email, one is created automatically.

The `display_name` and `handle` fields are optional and only used when creating a new account. Existing accounts ignore these fields.

### Step 2: Verify the Code

```
POST /v1/auth/verify
{
  "session_id": "sess_abc123",
  "code": "742819"
}
```

If the code is correct, the response includes your API key:

```json
{
  "account_id": "acct_xyz789",
  "handle": "yourhandle",
  "api_key": "lp_free_abc123...",
  "is_new_account": true,
  "gravity_level": 0,
  "next_level": "Verify your LinkedIn profile or domain to reach Gravity 1."
}
```

The API key is shown once. Store it securely — it can't be retrieved later.

## LinkedIn OAuth Flow

LinkedIn OAuth is the recommended authentication method because it simultaneously creates an account and verifies your LinkedIn identity, immediately reaching [Gravity 1](https://lightpaper.org/author-gravity-a-trust-system-for-the-agentic-web).

### Step 1: Start the Flow

```
POST /v1/auth/linkedin
```

The response includes an authorization URL:

```json
{
  "authorization_url": "https://www.linkedin.com/oauth/v2/authorization?...",
  "session_id": "sess_def456",
  "instructions": "Open the authorization URL in a browser..."
}
```

### Step 2: User Authorizes in Browser

The user (or the agent, by providing the URL) opens the authorization URL in a browser. LinkedIn asks for permission, and on approval, redirects back to lightpaper.org's callback URL.

### Step 3: Poll for Completion

The agent polls until the OAuth flow completes:

```
GET /v1/auth/linkedin/poll?session_id=sess_def456
```

```json
{
  "completed": true,
  "account_id": "acct_xyz789",
  "handle": "yourhandle",
  "api_key": "lp_free_abc123...",
  "gravity_level": 1
}
```

Notice the gravity level is already 1 — LinkedIn verification is automatic during OAuth login.

## How Agents Handle Auth

For AI agents, the recommended flow depends on the situation:

**First-time setup**: Use email OTP. The agent asks the user for their email, triggers the OTP, and asks the user to provide the code. No browser required.

**If the user has LinkedIn**: Use LinkedIn OAuth. The agent generates the authorization URL and asks the user to open it. The agent polls in the background until completion.

**Returning users**: The agent stores the API key (securely) and includes it in subsequent requests. No re-authentication needed.

The MCP server handles authentication automatically. If the API key is provided in the environment, all tools are pre-authenticated.

## API Key Management

API keys on lightpaper.org use distinct prefixes:

| Prefix | Meaning |
|--------|---------|
| `lp_free_` | Free tier account |
| `lp_live_` | Paid tier account |
| `lp_test_` | Test environment |

The prefix makes it easy to identify key types at a glance and prevents accidentally using test keys in production.

API keys are stored as [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) hashes in the database. The platform never stores plaintext keys. Authentication uses timing-safe comparison to prevent [timing attacks](https://en.wikipedia.org/wiki/Timing_attack).

## Security Considerations

Several security measures protect the authentication system:

- **OTP verification** uses `hmac.compare_digest()` for timing-safe comparison
- **OAuth callbacks** HTML-escape all output to prevent [XSS](https://owasp.org/www-community/attacks/xss/)
- **Rate limiting**: Auth endpoints are rate-limited to prevent brute-force attacks
- **Session expiry**: OTP sessions expire after 10 minutes
- **Email delivery**: Sent via [Resend](https://resend.com/) from `auth@lightpaper.org` with proper [SPF](https://en.wikipedia.org/wiki/Sender_Policy_Framework) and [DKIM](https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail) records

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [OAuth 2.0 specification](https://oauth.net/2/)
- [Resend — email for developers](https://resend.com/)
- [bcrypt — password hashing](https://en.wikipedia.org/wiki/Bcrypt)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
"""
})

# ── Post 9: Verifying Your Identity ──────────────────────────────────────────

POSTS.append({
    "title": "Verifying Your Identity",
    "subtitle": "Domain DNS, LinkedIn OAuth, ORCID, and credential verification on lightpaper.org",
    "tags": ["verification", "identity", "gravity", "credentials"],
    "content": r"""# Verifying Your Identity

Identity verification on lightpaper.org is how you build [Author Gravity](https://lightpaper.org/author-gravity-a-trust-system-for-the-agentic-web) — the trust signal that makes your content more discoverable. Three types of identity verification are available, plus agent-driven credential submission. Each works independently, and you can complete them in any order.

## Domain DNS Verification

Domain verification proves you control a specific domain. This is the strongest identity signal for organizations, companies, and bloggers who publish under their own domain.

### How It Works

**Step 1**: Request a verification challenge:

```
POST /v1/account/verify/domain
{
  "domain": "example.com"
}
```

The response includes a TXT record value:

```json
{
  "domain": "example.com",
  "txt_record": "lightpaper-verify=abc123def456",
  "instructions": "Add a TXT record to your DNS..."
}
```

**Step 2**: Add the TXT record to your domain's DNS settings. This is done through your domain registrar or DNS provider ([Cloudflare](https://www.cloudflare.com/), [Route 53](https://aws.amazon.com/route53/), [Google Domains](https://domains.google/), etc.).

**Step 3**: Check if the record has propagated:

```
GET /v1/account/verify/domain/check
```

DNS propagation typically takes a few minutes but can take up to 48 hours. The check endpoint queries DNS directly and returns whether verification succeeded.

Once verified, your domain appears as a badge on your published documents and contributes one identity toward your gravity level.

## LinkedIn OAuth Verification

LinkedIn verification confirms you have a real professional identity. It's the fastest verification method — just an OAuth flow that takes about 30 seconds.

If you authenticated via LinkedIn OAuth, your LinkedIn is already verified. This section covers verifying LinkedIn for accounts that were created via email OTP.

### How It Works

**Step 1**: Start the verification:

```
POST /v1/account/verify/linkedin
```

The response includes an authorization URL to open in a browser.

**Step 2**: Open the URL in a browser. LinkedIn asks for permission to share your basic profile information.

**Step 3**: On approval, LinkedIn redirects back to lightpaper.org's callback, which completes the verification.

**Step 4**: Check the result:

```
GET /v1/account/verify/linkedin/check
```

```json
{
  "verified": true,
  "gravity_level": 1
}
```

LinkedIn verification sets `verified_linkedin: true` on your account and contributes one identity toward gravity.

## ORCID Verification

[ORCID](https://orcid.org/) (Open Researcher and Contributor ID) is a persistent digital identifier for researchers. If you have an ORCID iD, linking it to your lightpaper.org account connects your publications to your scholarly identity.

### How It Works

```
POST /v1/account/verify/orcid
{
  "orcid_id": "0000-0002-1825-0097"
}
```

The system verifies that the ORCID exists by querying the [ORCID public API](https://pub.orcid.org/) and retrieves your registered name:

```json
{
  "verified": true,
  "gravity_level": 2,
  "orcid_name": "Josiah Carberry"
}
```

ORCID verification contributes one identity toward gravity. Combined with LinkedIn, that's gravity level 2 (1.25x search multiplier).

## Agent-Driven Credential Submission

Beyond identity verification, professional credentials earn points toward higher gravity levels. Credentials are submitted through the API with an evidence tier that reflects how well the claim has been verified.

### Credential Types

| Type | Examples |
|------|----------|
| Degree | BS Computer Science, PhD Physics, MBA |
| Certification | AWS Solutions Architect, CPA, PE |
| Employment | Software Engineer at Google, Professor at MIT |

### Evidence Tiers

| Tier | Points | When to Use |
|------|--------|-------------|
| Confirmed | 3 | Agent found strong external evidence (LinkedIn profile matches, university records, professional registry) |
| Supported | 2 | Partial evidence exists but isn't definitive |
| Claimed | 1 | User self-reported, no external verification |

### Submitting Credentials

```
POST /v1/account/credentials
{
  "credentials": [
    {
      "credential_type": "degree",
      "institution": "MIT",
      "title": "BS Computer Science",
      "year": 2018,
      "evidence_tier": "confirmed",
      "evidence_data": {
        "source": "LinkedIn profile",
        "url": "https://linkedin.com/in/example"
      },
      "agent_notes": "Degree confirmed on LinkedIn profile with matching graduation year."
    }
  ]
}
```

The response includes updated gravity information:

```json
{
  "credentials": [...],
  "gravity_level": 3,
  "gravity_badges": ["linkedin", "orcid", "degree:confirmed"],
  "credential_points": 3
}
```

### How Agents Should Approach Credentials

The most effective workflow for AI agents:

1. **Ask the user** about their background — degrees, certifications, current/past positions
2. **Research the claims** — check LinkedIn profiles, university websites, professional registries
3. **Assess evidence tier** honestly — don't inflate tiers without evidence
4. **Submit with notes** — the `agent_notes` field explains your reasoning for the evidence tier

This creates a trust chain: the user states their credentials, the agent verifies what it can, and the evidence tier reflects the actual strength of verification.

## Combining Verifications

Here are the most common paths to each gravity level:

**Gravity 1** (1.1x): Verify LinkedIn. One OAuth flow, 30 seconds.

**Gravity 2** (1.25x): LinkedIn + ORCID. Two minutes if you have an ORCID.

**Gravity 3** (1.4x): LinkedIn + confirmed degree. The agent verifies your degree via LinkedIn and submits it as "confirmed" (3 credential points).

**Gravity 4** (1.55x): LinkedIn + domain + confirmed degree. Or LinkedIn + two confirmed credentials (6 points).

**Gravity 5** (1.7x): Two identities + 6 credential points. For example: LinkedIn + ORCID + confirmed degree + confirmed employment.

## Checking Your Status

View your current gravity level and next steps:

```
GET /v1/account/gravity
```

The response includes context-sensitive advice about what verification would have the biggest impact on your gravity level.

## References

- [lightpaper.org API documentation](https://lightpaper.org/llms.txt)
- [ORCID — Open Researcher and Contributor ID](https://orcid.org/)
- [ORCID public API](https://pub.orcid.org/)
- [Cloudflare DNS management](https://www.cloudflare.com/)
- [OAuth 2.0 specification](https://oauth.net/2/)
"""
})

# ── Post 10: Markdown, Code Highlighting, and Footnotes ─────────────────────

POSTS.append({
    "title": "Markdown, Code Highlighting, and Footnotes",
    "subtitle": "Supported Markdown features and rendering on lightpaper.org",
    "tags": ["markdown", "formatting", "code", "writing"],
    "content": r"""# Markdown, Code Highlighting, and Footnotes

lightpaper.org renders Markdown to HTML using [markdown-it](https://github.com/markdown-it/markdown-it) with GFM (GitHub Flavored Markdown) extensions, [Pygments](https://pygments.org/) syntax highlighting, and [nh3](https://github.com/messense/nh3) HTML sanitization. This gives you a rich set of formatting options while keeping everything secure.

This post covers every supported Markdown feature with examples.

## Basic Formatting

Standard Markdown formatting works as expected:

- **Bold** with `**double asterisks**`
- *Italic* with `*single asterisks*`
- ~~Strikethrough~~ with `~~double tildes~~`
- `Inline code` with `` `backticks` ``
- [Links](https://lightpaper.org) with `[text](url)`

These are the building blocks. Most documents use all of them.

## Headings

Six levels of headings are supported:

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

Headings are extracted for the table of contents and used by the quality scoring algorithm. Using 3 or more headings earns the maximum structure points for heading hierarchy.

In the **paper** format, headings are automatically numbered (1, 1.1, 1.2, 2, etc.) to provide the academic section numbering readers expect.

## Code Blocks

Fenced code blocks with language identifiers get full [Pygments](https://pygments.org/) syntax highlighting. Over 500 languages are supported.

````markdown
```python
def publish(title, content):
    response = httpx.post(
        "https://lightpaper.org/v1/publish",
        json={"title": title, "content": content}
    )
    return response.json()
```
````

This renders with syntax-highlighted colors for keywords, strings, functions, and other language elements.

### Supported Languages

Some commonly used languages:

| Language | Identifier | Language | Identifier |
|----------|-----------|----------|-----------|
| Python | `python` | JavaScript | `javascript` or `js` |
| TypeScript | `typescript` or `ts` | Rust | `rust` |
| Go | `go` | Java | `java` |
| C/C++ | `c` / `cpp` | SQL | `sql` |
| Bash | `bash` or `shell` | JSON | `json` |
| YAML | `yaml` | HTML | `html` |
| CSS | `css` | Markdown | `markdown` |

If no language is specified, Pygments attempts to guess the language from the content. For the most reliable highlighting, always specify the language.

Code blocks contribute to the substance component of the [quality score](https://lightpaper.org/how-quality-scoring-works). Including 4+ code blocks earns 5 substance points, and 2-3 blocks earn 3 points.

## Tables

GFM-style tables are fully supported:

```markdown
| Feature | Supported |
|---------|-----------|
| Tables | Yes |
| Alignment | Yes |
| Nested formatting | Yes |
```

Tables support column alignment with colons:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| a    |   b    |     c |
```

Tables are wrapped in a scrollable container on mobile devices, so wide tables remain usable on small screens. Including tables in your content adds up to 4 points to your substance score.

## Task Lists

GFM task lists render as checkboxes:

```markdown
- [x] Create an account
- [x] Publish first document
- [ ] Verify LinkedIn
- [ ] Submit credentials
```

This renders as an interactive-looking checklist (the checkboxes are read-only in the rendered output). Task lists are useful for tutorials, checklists, and project status updates.

## Blockquotes

Standard blockquote syntax:

```markdown
> The web has a publishing problem. Getting words onto a permanent URL
> shouldn't require a CMS or a deployment pipeline.
```

In the **essay** format, blockquotes are styled as pull quotes with distinctive typography, making them useful for highlighting key passages.

Nested blockquotes work as well:

```markdown
> First level
>> Second level
>>> Third level
```

## Footnotes

lightpaper.org supports Markdown footnotes via the [markdown-it-footnote](https://github.com/markdown-it/markdown-it-footnote) plugin:

```markdown
This claim needs a source[^1]. And so does this one[^2].

[^1]: First reference — https://example.com
[^2]: Second reference with more detail about the source.
```

Footnotes render as superscript numbers in the text with a numbered footnote section at the bottom of the document. They're essential for academic writing and useful for any content that references external sources.

Footnotes contribute to the attribution score. Three or more footnotes earn 7 points; 1-2 earn 4 points.

## Horizontal Rules

Three or more hyphens, asterisks, or underscores on a line:

```markdown
---
```

This creates a visual separator between sections.

## Images

Standard Markdown image syntax:

```markdown
![Alt text](https://example.com/image.png "Optional title")
```

Images are sanitized to allow only `http`, `https`, and `mailto` URL schemes. The `alt`, `title`, `width`, and `height` attributes are preserved.

## Lists

Both ordered and unordered lists are supported, including nested lists:

```markdown
1. First item
   - Nested bullet
   - Another nested item
2. Second item
3. Third item

- Bullet one
- Bullet two
  1. Nested numbered
  2. Another nested
```

List items contribute to substance scoring. Five or more list items earn 4 points; 2-4 earn 2 points.

## HTML Sanitization

All rendered HTML passes through [nh3](https://github.com/messense/nh3), a Rust-based HTML sanitizer. This means:

- Only [whitelisted HTML tags](https://github.com/nickt/nh3) are preserved (headings, paragraphs, links, code, tables, etc.)
- JavaScript is stripped entirely — no `<script>` tags, no `onclick` handlers, no `javascript:` URLs
- Link attributes automatically include `rel="noopener noreferrer"` for security
- CSS `style` attributes are restricted to safe properties
- Only `http`, `https`, and `mailto` URL schemes are allowed

This means you can't embed arbitrary HTML, but it also means published content is safe from [XSS attacks](https://owasp.org/www-community/attacks/xss/). The sanitization happens server-side after Markdown rendering, so there's no way to bypass it.

## Formatting Tips for Quality

To maximize your quality score through formatting:

1. **Use 3+ headings** for structure (10 points)
2. **Include code blocks** for substance (up to 5 points)
3. **Add tables** where data is tabular (up to 4 points)
4. **Use footnotes** for citations (up to 7 attribution points)
5. **Add a References section** heading (8 attribution points)
6. **Vary paragraph lengths** for natural rhythm (up to 7 structure points)

## References

- [markdown-it — Markdown parser](https://github.com/markdown-it/markdown-it)
- [Pygments — syntax highlighter](https://pygments.org/)
- [nh3 — HTML sanitizer](https://github.com/messense/nh3)
- [GitHub Flavored Markdown specification](https://github.github.com/gfm/)
- [CommonMark specification](https://commonmark.org/)
"""
})

# ── Publish all posts ────────────────────────────────────────────────────────

def publish_post(client, post_data):
    """Publish a single post and return the response."""
    payload = {
        "title": post_data["title"],
        "subtitle": post_data["subtitle"],
        "content": post_data["content"],
        "format": "post",
        "authors": [AUTHOR],
        "tags": post_data["tags"],
        "options": {"listed": True},
    }
    resp = client.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    return resp

def main():
    results = []
    with httpx.Client() as client:
        for i, post in enumerate(POSTS, 1):
            print(f"\n{'='*60}")
            print(f"Publishing {i}/10: {post['title']}")
            print(f"{'='*60}")

            resp = publish_post(client, post)

            if resp.status_code == 201:
                data = resp.json()
                results.append({
                    "title": post["title"],
                    "url": data["url"],
                    "permanent_url": data["permanent_url"],
                    "quality_score": data["quality_score"],
                    "quality_breakdown": data["quality_breakdown"],
                    "word_count": data["word_count"],
                })
                print(f"  URL: {data['url']}")
                print(f"  Quality: {data['quality_score']} (S:{data['quality_breakdown']['structure']} "
                      f"Sub:{data['quality_breakdown']['substance']} "
                      f"T:{data['quality_breakdown']['tone']} "
                      f"A:{data['quality_breakdown']['attribution']})")
                print(f"  Words: {data['word_count']}")
                if data.get("quality_suggestions"):
                    print(f"  Suggestions: {', '.join(data['quality_suggestions'])}")
            else:
                print(f"  ERROR {resp.status_code}: {resp.text}")
                results.append({
                    "title": post["title"],
                    "error": f"{resp.status_code}: {resp.text}",
                })

            # Small delay between publishes to be polite
            time.sleep(1)

    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        if "error" in r:
            print(f"  FAIL: {r['title']} — {r['error'][:80]}")
        else:
            print(f"  OK: {r['title']}")
            print(f"      {r['url']} (quality: {r['quality_score']}, words: {r['word_count']})")

if __name__ == "__main__":
    main()
