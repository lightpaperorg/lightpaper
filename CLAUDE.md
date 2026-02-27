# lightpaper.org — Claude Code Instructions

## Architecture

FastAPI + async SQLAlchemy + PostgreSQL 16. Single-process async app deployed on Google Cloud Run.

### Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, middleware (CORS, security headers, body size, rate limiting) |
| `app/config.py` | Pydantic settings from env vars |
| `app/auth.py` | Firebase + API key dual authentication |
| `app/models.py` | SQLAlchemy ORM models (8 tables) |
| `app/schemas.py` | Pydantic request/response schemas with size limits |
| `app/rate_limit.py` | slowapi limiter singleton |
| `app/utils.py` | get_client_ip() for Cloud Run proxy |
| `app/routes/publish.py` | POST /v1/publish — the core endpoint |
| `app/routes/search.py` | GET /v1/search — full-text + gravity ranking |
| `app/routes/documents.py` | CRUD /v1/documents/{id} |
| `app/routes/reading.py` | GET /{slug} — content negotiation (HTML/JSON) |
| `app/routes/discovery.py` | robots.txt, sitemap.xml, llms.txt, OG images |
| `app/services/renderer.py` | markdown-it-py + nh3 HTML sanitization |
| `app/services/quality.py` | Deterministic quality scoring (0-100) |
| `app/services/gravity.py` | Author verification levels (0-3) |
| `app/services/slug.py` | URL slug generation + reserved slug list |
| `app/services/og_image.py` | Pillow-based OG image generation |
| `mcp/server.py` | MCP server with 5 tools |
| `init.sql` | Database schema (11 tables) |

## Running Locally

```bash
docker compose up -d db
cp .env.example .env
pip install -r requirements-dev.txt
uvicorn app.main:app --port 8001 --reload
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Security-Sensitive Areas

- **`app/services/renderer.py`**: HTML sanitized via nh3 after markdown rendering. Never bypass or use `|safe` without sanitization.
- **`app/routes/search.py`**: JSONB filters use `sqlalchemy.cast()` — never use f-strings for SQL.
- **`app/templates/document.html`**: JSON-LD uses `|tojson` filter — never use raw `{{ var }}` inside `<script>` blocks.
- **`app/auth.py`**: API key lookup uses bcrypt — timing-safe comparison.
- **`app/services/slug.py`**: Reserved slugs prevent squatting of platform paths.

## Deployment

```bash
# Build + deploy to Cloud Run
bash deploy/deploy-cloud-run.sh
```

## Gotchas

- **Catch-all route**: `/{slug:path}` in reading.py must be the LAST router mounted.
- **`metadata` is a reserved name**: SQLAlchemy model uses `doc_metadata` to avoid collision.
- **Rate limiter**: Imported from `app/rate_limit.py` (not `app/main.py`) to avoid circular imports.
- **Body size limit**: 2MB enforced by middleware — large documents will get 413.
- **Version limit**: 100 versions per document — returns 422 when exceeded.
- **Content size**: max 500K chars in content field, enforced by Pydantic schema.
