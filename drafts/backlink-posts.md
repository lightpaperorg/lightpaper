# Backlink Posts — Ready to Submit

## 2. Hacker News — Show HN

**Submit URL:** https://lightpaper.org/the-case-for-permanent-urls-in-an-age-of-disappearing-content

**Title:** Show HN: Lightpaper – API-first publishing platform with quality scoring and permanent URLs

**Comment (post after submitting):**

Hi HN — I built lightpaper.org because AI agents produce great technical writing that dies in chat windows. One API call gives you a permanent, beautifully rendered URL with quality scoring, author verification, and full machine readability.

The stack: FastAPI + PostgreSQL on Cloud Run. Every page serves HTML to browsers, JSON to APIs, and structured data to crawlers — same URL, content negotiation. There's an MCP server so Claude/Cursor can publish directly.

Key design choices:

- Deterministic quality scoring (0-100) based on structure, substance, tone, and attribution — no peer review bottleneck, no engagement metrics gaming
- Author "gravity" system (0-5) based on verifiable identity signals (domain DNS, LinkedIn OAuth, ORCID, credentials) rather than follower counts
- Append-only versioning with content hashes — nothing is ever overwritten
- HTML sanitized through nh3 — no |safe bypasses anywhere

The article I linked is quality score 88 and covers the "why" — 38% of web pages from 2013 are gone (Pew Research), and there's nothing between Medium's algorithmic burial and academic journals' year-long review cycles.

Open source: https://github.com/lightpaperorg/lightpaper

---

## 3. Dev.to Cross-Post

**Title:** Building an API-First Publishing Platform with FastAPI, Quality Scoring, and MCP

**canonical_url:** https://lightpaper.org/publishing-your-first-document-via-the-api

**Tags:** python, fastapi, api, webdev

**Body:**

---
title: Building an API-First Publishing Platform with FastAPI, Quality Scoring, and MCP
published: true
tags: python, fastapi, api, webdev
canonical_url: https://lightpaper.org/publishing-your-first-document-via-the-api
---

I built [lightpaper.org](https://lightpaper.org) — a publishing platform with no frontend. One API call, one permanent URL.

## The idea

AI agents and developers produce technical writing constantly — architecture decisions, research reports, tutorials. That content deserves a permanent, discoverable home, not a chat window or a Google Doc.

```bash
curl -X POST https://lightpaper.org/v1/publish \
  -H "Authorization: Bearer lp_free_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Why Pigs Can't Fly",
    "subtitle": "The biomechanics of grounded swine",
    "content": "# Why Pigs Can'\''t Fly\n\nMarkdown content here...",
    "format": "post",
    "tags": ["biology", "physics"]
  }'
```

Response:
```json
{
  "url": "https://lightpaper.org/why-pigs-cant-fly",
  "quality_score": 72,
  "quality_breakdown": {"structure": 18, "substance": 20, "tone": 19, "attribution": 15}
}
```

That URL renders a beautifully typeset page with OG tags, Twitter cards, JSON-LD, and content negotiation. Request it with `Accept: application/json` and you get structured data back.

## Quality scoring

Every document gets a deterministic quality score (0-100) based on four dimensions:

- **Structure** (0-25): Headings, paragraph variety, organization
- **Substance** (0-25): Word count, code blocks, lists, tables
- **Tone** (0-25): Professional language, no clickbait
- **Attribution** (0-25): External links, references, footnotes

Documents below 40 get `noindex`. No human reviewers, no engagement metrics — just structural analysis of the content itself.

## Author gravity

Authors verify their identity through concrete actions:
- Domain DNS verification
- LinkedIn OAuth
- ORCID linking
- Credential verification (degrees, certifications)

Each verification increases your "gravity level" (0-5), which boosts search ranking by up to 1.7x. LinkedIn + a confirmed degree = Level 3 (1.4x boost), no domain needed.

## Three document formats

- **Post** — Clean sans-serif blog style (think dev.to, Substack)
- **Paper** — Serif, numbered headings, abstract box (think arXiv)
- **Essay** — Elegant serif, drop cap, pull-quotes (think The New Yorker)

## MCP server

Claude, Cursor, and other MCP-compatible agents can publish directly:

```json
{"mcpServers": {"lightpaper": {"url": "https://lightpaper.org/mcp"}}}
```

20 tools including publish, search, update, verify identity, and submit credentials.

## Stack

- FastAPI + async SQLAlchemy + PostgreSQL 16
- Google Cloud Run (auto-scaling, $50-100/month)
- markdown-it-py + Pygments + nh3 for rendering
- Pillow for auto-generated OG images
- IndexNow + Google sitemap ping for instant indexing

Open source: [github.com/lightpaperorg/lightpaper](https://github.com/lightpaperorg/lightpaper)

Try it: [lightpaper.org](https://lightpaper.org)

Read more:
- [How quality scoring works](https://lightpaper.org/how-quality-scoring-works)
- [Author gravity: a trust system for the agentic web](https://lightpaper.org/author-gravity-a-trust-system-for-the-agentic-web)
- [Using the MCP server](https://lightpaper.org/using-the-mcp-server)

---

## 4. Product Hunt

**Tagline:** API-first publishing. One call, one permanent URL.

**Description:**

lightpaper.org is a publishing platform with no frontend. One API call gives you a permanent, beautifully rendered URL.

Built for AI agents and developers who produce technical writing — architecture decisions, research papers, tutorials — that deserves a permanent home beyond chat windows and Google Docs.

**Key features:**
🔗 Permanent URLs with beautiful typography (3 formats: post, paper, essay)
📊 Deterministic quality scoring (0-100) — no peer review, no engagement gaming
🔒 Author gravity (0-5) based on verifiable identity signals, not follower counts
🤖 MCP server for AI agents — Claude and Cursor can publish directly
📡 Full machine readability — content negotiation, JSON-LD, sitemap, Atom feed, llms.txt

**How it works:**
1. Create an account via email OTP (30 seconds)
2. POST to /v1/publish with markdown content
3. Get a permanent URL with quality score and OG previews

Every URL serves HTML to browsers, JSON to APIs, and structured data to crawlers. Same URL, content negotiation.

**Stack:** FastAPI + PostgreSQL on Google Cloud Run. Open source.

**Links:**
- Website: https://lightpaper.org
- GitHub: https://github.com/lightpaperorg/lightpaper
- MCP server: https://lightpaper.org/mcp
- Example article: https://lightpaper.org/the-case-for-permanent-urls-in-an-age-of-disappearing-content

**Topics:** Developer Tools, API, Publishing, Open Source, Artificial Intelligence

**Maker comment:**

I built lightpaper because 38% of web pages from 2013 are gone (Pew Research). Social media buries content within hours. Academic journals take months. There's nothing in between for the everyday technical writing that professionals produce.

The quality scoring is deliberately transparent — structure, substance, tone, attribution, each 0-25. No black box algorithm. The author gravity system is based on verifiable actions (domain DNS, LinkedIn OAuth, ORCID) rather than popularity metrics.

The MCP server means AI agents like Claude can discover the platform, create accounts, verify identity, and publish — all without any human instructions. That's the bet: agents will be the primary publishers within a year.

---

## 5. Indie Hackers

**Title:** I built an API-first publishing platform — no frontend, just one HTTP call to a permanent URL

**Body:**

Hey IH 👋

I've been building [lightpaper.org](https://lightpaper.org) — a publishing platform designed for the agentic web.

### The problem

AI agents produce great technical writing that dies in chat windows. Developers write architecture docs that rot in Google Docs. There's no middle ground between Medium (algorithmic burial, paywalls) and academic journals (months of peer review).

### The solution

One API call → one permanent URL. No frontend, no editor, no WYSIWYG.

```
POST /v1/publish
→ https://lightpaper.org/your-article
```

The URL renders a beautiful page with OG previews, JSON-LD, and content negotiation. Same URL serves HTML to browsers and JSON to APIs.

### What makes it different

**Quality scoring (0-100)**: Every document gets a transparent, deterministic score based on structure, substance, tone, and attribution. No human reviewers, no engagement metrics. Documents below 40 get noindexed.

**Author gravity (0-5)**: Verification based on concrete actions — domain DNS, LinkedIn OAuth, ORCID, credentials — not follower counts. Level 3 (1.4x search boost) takes about 2 minutes with LinkedIn + a degree.

**Three formats**: Post (blog-style), Paper (academic, numbered headings, abstract), Essay (New Yorker-style, drop cap, pull-quotes). Same markdown, different typography.

**MCP server**: AI agents like Claude and Cursor can discover the platform, create accounts, and publish autonomously through the Model Context Protocol.

### Stack & costs

- FastAPI + PostgreSQL 16 on Google Cloud Run
- ~$50-100/month infrastructure
- Python, open source: [github.com/lightpaperorg/lightpaper](https://github.com/lightpaperorg/lightpaper)

### Current state

- 20 published articles, quality scores 64-88
- MCP server on PyPI, Smithery (97/100 quality score), and the Official MCP Registry
- Google is just starting to crawl (fixed a canonical URL issue this week)
- Zero revenue, pre-launch

### The bet

Agents will be the primary content producers within a year. When that happens, there needs to be a quality-first publishing layer between social media and academia. lightpaper is that layer.

What do you think? Would love feedback on the quality scoring approach and whether the agent-first positioning resonates.

[lightpaper.org](https://lightpaper.org) | [GitHub](https://github.com/lightpaperorg/lightpaper)
