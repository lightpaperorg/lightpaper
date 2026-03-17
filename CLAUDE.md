# lightpaper.org — Claude Code Instructions

## Architecture

FastAPI + async SQLAlchemy + PostgreSQL 16. Single-process async app deployed on Google Cloud Run.

### Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, middleware (CORS, security headers, body size, rate limiting) |
| `app/config.py` | Pydantic settings from env vars |
| `app/auth.py` | API key + email OTP + LinkedIn OAuth authentication |
| `app/models.py` | SQLAlchemy ORM models (18 tables) |
| `app/schemas.py` | Pydantic request/response schemas with size limits |
| `app/rate_limit.py` | slowapi limiter singleton |
| `app/utils.py` | get_client_ip() for Cloud Run proxy |
| `app/routes/publish.py` | POST /v1/publish — the core endpoint |
| `app/routes/search.py` | GET /v1/search — full-text + gravity ranking |
| `app/routes/documents.py` | CRUD /v1/documents/{id}, notifies search engines on update/delete |
| `app/routes/books.py` | Book publishing: POST /v1/books, chapter management |
| `app/routes/write.py` | Writing IDE API: sessions, chat, files, publish |
| `app/routes/ide.py` | Serves the React SPA at /write |
| `app/services/wave_engine.py` | Wave Method system prompts per wave |
| `app/ide/` | React + Vite frontend for the Writing IDE |
| `app/routes/reading.py` | GET /{slug}, GET /books/{slug} — content negotiation (HTML/JSON) |
| `app/routes/discovery.py` | robots.txt, sitemap.xml, feed.xml, llms.txt, OG images, IndexNow + Google ping |
| `app/routes/auth.py` | Email OTP + LinkedIn OAuth login/signup endpoints |
| `app/routes/linkedin.py` | LinkedIn OAuth verification for existing accounts |
| `app/routes/verification.py` | Domain DNS, ORCID verification, gravity status |
| `app/routes/credentials.py` | Agent-driven credential verification |
| `app/routes/narration.py` | Audiobook narration: estimate, create, status, callback |
| `app/services/narration.py` | ElevenLabs TTS, markdown→plaintext, GCS upload |
| `app/services/renderer.py` | markdown-it-py + nh3 HTML sanitization |
| `app/services/quality.py` | Deterministic quality scoring (0-100) |
| `app/services/gravity.py` | Non-hierarchical author gravity (0-5) |
| `app/services/slug.py` | URL slug generation + reserved slug list |
| `app/services/og_image.py` | Pillow-based OG image generation |
| `app/services/api_keys.py` | API key generation utility |
| `app/services/email.py` | Resend API email delivery for OTP |
| `mcp/server.py` | MCP server with 24 tools + 3 prompts (stdio transport) |
| `app/routes/mcp_http.py` | Remote MCP endpoint (Streamable HTTP transport at /mcp) |
| `lightpaper_mcp/` | Standalone PyPI package for MCP server distribution |
| `AGENTS.md` | OpenAI AGENTS.md standard — project-level agent instructions |
| `init.sql` | Database schema (13 tables) |
| `migrations/*.sql` | Idempotent SQL migrations (run at startup) |

## Running Locally

```bash
docker compose up -d db
cp .env.example .env
pip install -r requirements-dev.txt
uvicorn app.main:app --port 8001 --reload
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

Note: ~7 tests require PostgreSQL on port 5433 (`docker compose up -d db`). The remaining ~58 tests pass without a database (including test_gravity.py with 42 gravity unit tests).

## Indexing & Discovery

Search engine notifications fire automatically on publish, update, and delete:
- **IndexNow**: Bing, Yandex, DuckDuckGo, Seznam — instant URL submission
- **Google sitemap ping**: `GET https://www.google.com/ping?sitemap=...` triggers re-crawl
- **Atom feed**: `GET /feed.xml` — 50 most recent listed documents
- **Sitemap**: `GET /sitemap.xml` — all listed documents with quality >= 40, plus author profiles
- **robots.txt**: References sitemap.xml and llms.txt
- **llms.txt**: Full agent instructions including onboarding flow, API reference, gravity system
- **ai-plugin.json**: OpenAI plugin manifest at `/.well-known/ai-plugin.json`
- **MCP server card**: `/.well-known/mcp/server-card.json` — config schema for Smithery/registries
- **MCP registry auth**: `/.well-known/mcp-registry-auth` — ed25519 public key for Official MCP Registry HTTP auth
- **A2A agent card**: `/.well-known/agent.json` — Google A2A protocol
- **HTML meta**: OG tags, Twitter cards, JSON-LD structured data, canonical URLs, noindex for quality < 40
- **OG images**: Auto-generated per document at `/og/{doc_id}.png`

Implementation: `notify_search_engines()` in discovery.py, called from publish.py, documents.py.

## Author Gravity (non-hierarchical)

Verifications are independent — any combination reaches any level:

| Level | Requirement | Multiplier |
|-------|------------|-----------|
| 0 | Nothing | 1.0x |
| 1 | Any 1 identity (domain, LinkedIn, or ORCID) | 1.1x |
| 2 | 2 identities | 1.25x |
| 3 | 3 ids, OR 2 ids + 1 cred pt, OR 1 id + 3 cred pts | 1.4x |
| 4 | 2+ ids + 3 cred pts, OR 1 id + 6 cred pts | 1.55x |
| 5 | 2+ ids + 6 cred pts | 1.7x |

Key: LinkedIn + confirmed degree (3 pts) = Level 3. No domain or ORCID needed.

`get_next_level_instructions()` takes verification state and gives context-sensitive advice.

## Authentication

Two auth flows, no anonymous publishing. Auth uses `Authorization: Bearer <api_key>` header (HTTPBearer scheme, NOT `X-API-Key`).

- **Email OTP**: `POST /v1/auth/email` sends code via Resend (`auth@lightpaper.org`), `POST /v1/auth/verify` returns API key
- **LinkedIn OAuth login**: `POST /v1/auth/linkedin` returns auth URL, browser callback, agent polls `/v1/auth/linkedin/poll`
- **LinkedIn verification** (for existing accounts): `POST /v1/account/verify/linkedin` — also sets `verified_linkedin=True`
- Email delivery: **Resend** (resend.com), domain `lightpaper.org` verified
- LinkedIn redirect URIs: `/v1/auth/linkedin/callback` (login) and `/v1/account/verify/linkedin/callback` (verification)
- API key prefixes: `lp_free_`, `lp_live_`, `lp_test_`

## Books

Books are ordered collections of chapters with a landing page, table of contents, and chapter navigation.

### URL Structure
| URL | What |
|-----|------|
| `/books/{book-slug}` | Book landing page (HTML) or JSON (content negotiation) |
| `/{chapter-slug}` | Chapter with prev/next nav (existing catch-all) |
| `/d/{doc_id}` | Permanent chapter link (existing, with nav context) |

Chapter slugs: `{book-slug}-ch{N}-{chapter-title-slug}`

### API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST /v1/books` | Publish complete book (all chapters at once) |
| `GET /v1/books/{book_id}` | Get book metadata + chapter listing |
| `PUT /v1/books/{book_id}` | Update book metadata |
| `DELETE /v1/books/{book_id}` | Soft-delete book + all chapters |
| `POST /v1/books/{book_id}/chapters` | Add a chapter |
| `PUT /v1/books/{book_id}/chapters/reorder` | Reorder chapters |
| `DELETE /v1/books/{book_id}/chapters/{doc_id}` | Detach chapter (doc survives) |

### Database
- `books` table: metadata, aggregated quality/word count, search_vector
- `book_chapters` table: ordered links between books and documents
- `documents.book_id`: denormalized FK for efficient chapter detection in reading route

### Key Details
- Chapters need 100+ words (relaxed from 300 for standalone docs) and at least one heading
- Book quality = weighted average of chapter scores + multi-chapter bonus (up to 5 points)
- Books appear in sitemap (priority 0.8), atom feed, and search (type=book|all)
- OG images show "Book · N chapters" at `/og/book_{id}.png`
- MCP: `publish_book`, `get_book`, `update_book` tools + `write-book` prompt

## Audiobook Narration

Premium feature: Pro users can convert published books into audiobooks via ElevenLabs.

### Flow
1. `POST /v1/narration/estimate` — character count + price per chapter
2. `POST /v1/narration/create` — creates Stripe one-time checkout (or manual start)
3. Payment completes → ElevenLabs Studio auto-converts
4. `POST /v1/narration/callback/{token}` — downloads audio, uploads to GCS
5. `GET /v1/narration/{id}` — check status + get audio URLs
6. Audio player appears on chapter reading pages

### Database
- `narrations` table: status tracking, Stripe/ElevenLabs IDs, callback token
- `narration_chapters` table: per-chapter audio URLs, duration, character count

### Key Details
- 10 curated voices (ElevenLabs premade voices)
- `max_chapters` param to narrate a subset of chapters
- `POST /v1/narration/start/{id}` manual start endpoint (bypasses Stripe for testing)
- Callback token is 32-byte hex — unguessable, no auth needed on callback
- Audio stored in GCS: `gs://{bucket}/narrations/{narration_id}/ch{N}.mp3`
- CSP includes `media-src https://storage.googleapis.com` for reading pages
- MCP: `narrate_book` tool with actions: voices, estimate, create, status
- Config: `ELEVENLABS_API_KEY`, `GCS_AUDIO_BUCKET`, `NARRATION_COST_PER_CHAR`

## Writing IDE (Wave Method)

A React frontend at `/write` that guides authors through the Wave Method — a structured book-writing process.

### The Wave Method
| Wave | Name | Output |
|------|------|--------|
| 0 | Raw Capture | Author dumps ideas, agent asks clarifying questions, produces chapter structure |
| 1 | Architecture | Scene-level outline for every chapter |
| 2 | Voice & Texture | Opening 500-800 words of every chapter |
| 3 | Pivotal Scenes | 8-10 load-bearing scenes in full polished form |
| 4 | Full Draft | Complete linear draft incorporating previous waves |
| 5+ | Edit Waves | Open-ended editorial passes directed by the author |

### Tech Stack
- **Frontend**: React + TypeScript + Vite, built to `app/ide/dist/`, served by FastAPI at `/write`
- **Backend**: `/v1/write/*` API endpoints with cookie-based session auth
- **AI**: Claude Opus 4.6 with extended thinking, 1M context (`context-1m-2025-08-07`), 128K output (`output-128k-2025-02-19`)
- **Tools**: `save_file`, `read_file`, `research`, `web_search`, `web_fetch` — executed in parallel via `asyncio.gather`
- **Database**: `writing_sessions`, `writing_files`, `writing_messages` tables (migration 015)
- **Build**: `cd app/ide && npm run build` — output served as static files by `app/routes/ide.py`
- **PWA**: manifest.json, service worker, app icons in `app/ide/public/`. Installable as standalone app.

### Key Details
- Cookie auth (`lp_session`) is separate from API Bearer auth — set on login via `/v1/write/auth/login`
- Claude uses `save_file` and `read_file` tools to create/review manuscript files during chat
- System prompts in `app/services/wave_engine.py` change per wave, include file inventory
- Context management: older messages condensed to summaries, recent 200 kept in full
- Publish endpoint assembles chapter files and calls the existing book publishing pipeline
- `write` is a reserved slug in `app/services/slug.py` and `app/routes/reading.py`
- CSP middleware in `app/main.py` allows inline scripts for `/write` paths
- Mobile: tab-based layout (Chat/Manuscript), slide-out file drawer, safe area insets
- Config: `ANTHROPIC_API_KEY`, `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `IDE_SESSION_SECRET`

## Security-Sensitive Areas

- **`app/services/renderer.py`**: HTML sanitized via nh3 after markdown rendering. Never bypass or use `|safe` without sanitization.
- **`app/routes/search.py`**: JSONB filters use `sqlalchemy.cast()` — never use f-strings for SQL.
- **`app/templates/document.html`**: JSON-LD uses `|tojson` filter — never use raw `{{ var }}` inside `<script>` blocks.
- **`app/auth.py`**: API key lookup uses bcrypt — timing-safe comparison.
- **`app/routes/auth.py`**: OTP verification uses `hmac.compare_digest()`. OAuth callback HTML-escapes all output.
- **`app/routes/linkedin.py`**: `_result_page()` uses `html.escape()` on all parameters.
- **`app/services/slug.py`**: Reserved slugs prevent squatting of platform paths.
- **`app/routes/write.py`**: IDE session cookie uses HMAC-SHA256 signing. `HttpOnly; Secure; SameSite=Lax`. Directory traversal protection in `ide.py`.

## Deployment

```bash
# Build + deploy to Cloud Run
GCP_PROJECT_ID=refreshing-rune-471208-e5 bash deploy/deploy-cloud-run.sh
```

Secrets managed via Google Secret Manager: `lightpaper-db-url`, `resend-api-key`, `linkedin-client-id`, `linkedin-client-secret`.

To update a secret without rebuilding: `gcloud run services update lightpaper --project=refreshing-rune-471208-e5 --region=us-central1 --update-secrets="SECRET_NAME=secret-name:latest"`

Database migrations run automatically at startup from the `migrations/` directory (idempotent SQL, executed per-statement).

## Gotchas

- **Two repo directories**: `/Users/jon/lightpaper/` (outer, deploy context) and `/Users/jon/lightpaper/lightpaper/` (inner, git repo). Files must be synced to outer before deploy. Deploy script runs from outer dir.
- **MCP session on Cloud Run**: `StreamableHTTPSessionManager` must use `stateless=True` because Cloud Run routes requests to different instances (in-memory sessions break).
- **MCP path matching**: Custom `MCPRoute(BaseRoute)` needed because Starlette's `Mount` redirects POST /mcp → /mcp/ (307), breaking MCP clients.
- **Catch-all route**: `/{slug:path}` in reading.py must be the LAST router mounted.
- **`metadata` is a reserved name**: SQLAlchemy model uses `doc_metadata` to avoid collision.
- **Rate limiter**: Imported from `app/rate_limit.py` (not `app/main.py`) to avoid circular imports.
- **Lazy imports for discovery**: `notify_search_engines` imported lazily in publish.py and documents.py to avoid circular deps.
- **Body size limit**: 2MB enforced by middleware — large documents will get 413.
- **Version limit**: 100 versions per document — returns 422 when exceeded.
- **Content size**: max 500K chars in content field, enforced by Pydantic schema.
- **Migrations**: SQL files in `migrations/` run at startup, per-statement with individual transactions. Use `IF NOT EXISTS`/`IF EXISTS` for idempotency.
- **Cloud SQL**: Private VPC only, no public IP. Migrations must run via app startup (not local scripts).
- **Python 3.12**: Codebase uses `str | None` union syntax — requires 3.10+, targets 3.12.

## MCP Distribution

| Channel | Identifier | Notes |
|---------|-----------|-------|
| Official MCP Registry | `org.lightpaper/lightpaper-mcp` | Canonical source; Cursor, Claude, PulseMCP auto-ingest |
| PyPI | `lightpaper-mcp` v0.1.1 | `pip install lightpaper-mcp` |
| Smithery | `@lightpaper/lightpaper` | 97/100 quality score, proxy: `https://lightpaper--lightpaper.run.tools` |
| Remote endpoint | `https://lightpaper.org/mcp` | Streamable HTTP, stateless, no install needed |
| mcp.so | Submitted | Web directory |
| Glama / awesome-mcp-servers | PR #2710 | Auto-syncs to glama.ai |

To update PyPI + registry: bump version in `lightpaper_mcp/pyproject.toml` + `server.json`, rebuild (`python3 -m build`), upload (`twine upload dist/*`), publish (`mcp-publisher publish`).

## Published Blog Content

10 introductory blog posts published on lightpaper.org (quality 69-85, format "post", author: Jon Gregory / jongregory):

| Post | URL |
|------|-----|
| What Is lightpaper.org? | `/what-is-lightpaper-org` |
| Three Document Formats: Post, Essay, and Paper | `/three-document-formats-post-essay-and-paper` |
| How Quality Scoring Works | `/how-quality-scoring-works` |
| Author Gravity: A Trust System for the Agentic Web | `/author-gravity-a-trust-system-for-the-agentic-web` |
| Publishing Your First Document via the API | `/publishing-your-first-document-via-the-api` |
| Using the MCP Server | `/using-the-mcp-server` |
| Search, Discovery, and SEO | `/search-discovery-and-seo` |
| Authentication Without Passwords | `/authentication-without-passwords` |
| Verifying Your Identity | `/verifying-your-identity` |
| Markdown, Code Highlighting, and Footnotes | `/markdown-code-highlighting-and-footnotes` |

These posts serve as SEO content, user documentation, and platform demonstration. Source script: `publish_blog_posts.py`.
