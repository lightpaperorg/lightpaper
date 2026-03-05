# Changelog

All notable changes to lightpaper.org are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] - 2026-03-04

### Added
- **MCP distribution**: Published `lightpaper-mcp` to PyPI, Official MCP Registry, Smithery (97/100 quality score), Glama, mcp.so
- **Streamable HTTP transport**: Single `/mcp` endpoint replacing deprecated SSE `/mcp/sse` — works with Smithery and all modern MCP clients
- **Tool annotations**: All 20 MCP tools annotated with `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`, and `title`
- **MCP server card**: `/.well-known/mcp/server-card.json` for registry config schema discovery
- **MCP Registry auth**: `/.well-known/mcp-registry-auth` endpoint for Official MCP Registry domain verification
- **Glama manifest**: `glama.json` at repo root for Glama directory submission

### Changed
- Upgraded `mcp` dependency from 1.3.0 to >=1.8.0
- MCP transport uses `stateless=True` for Cloud Run multi-instance compatibility
- Custom `MCPRoute` avoids Starlette `Mount` redirect (POST /mcp → /mcp/ 307)
- Added missing parameter descriptions to nested MCP tool schemas

### Fixed
- MCP endpoint returning 405 on POST when `json_response=True` (reverted to `False`)
- Session ID errors on Cloud Run due to in-memory session tracking across instances

## [0.1.0] - 2026-03-04

### Added
- **Blog content**: 10 introductory posts covering platform overview, formats, quality scoring, gravity, API tutorial, MCP server, search/SEO, auth, verification, and markdown features
- **Distribution channels**: PyPI package (`lightpaper-mcp`), remote SSE endpoint, JSON feed, Smithery listing, A2A agent card, AGENTS.md
- **Credential badges**: Clickable LinkedIn/ORCID badges with titles on author profiles
- **Three document formats**: Paper, essay, and post — each with distinct quality expectations and templates

### Changed
- Improved agent instruction gaps identified from 30-prompt end-to-end trace
- Search browsing and format update handling refinements

### Fixed
- Tags bug in document updates
- Agent flow gaps in format selection, search, and credential verification

## [0.0.3] - 2026-03-03

### Added
- **Non-hierarchical gravity**: Any combination of identities + credentials can reach any level (LinkedIn + confirmed degree = Level 3)
- **Google sitemap ping**: Automatic `GET google.com/ping?sitemap=...` on publish/update/delete
- **Atom feed**: `/feed.xml` with 50 most recent listed documents
- **Email OTP + LinkedIn OAuth**: Full authentication system replacing anonymous posting
- **Startup migration runner**: SQL migrations auto-execute at app startup
- **Brand images**: Logo and cover art

### Changed
- Authentication now required to publish — no more anonymous posting
- Gravity system rewritten from hierarchical tiers to non-hierarchical formula

### Fixed
- XSS vulnerability in credential rendering

## [0.0.2] - 2026-02-28

### Added
- **IndexNow**: Instant URL submission to Bing, DuckDuckGo, Yandex, Seznam on publish
- **Agent discovery**: `ai-plugin.json`, `robots.txt` with LLMs-txt reference, HTML link tags
- **llms.txt**: Prescriptive agent publishing guide at `/llms.txt`
- **MCP prompts**: Getting-started prompts and install instructions on landing page
- **Author profiles**: Public profile pages with published document listings
- **Document format templates**: Guided publishing for papers, essays, and posts
- **GitHub Actions CI**: Lint, test, and auto-deploy to Cloud Run on push to main

### Changed
- Landing page redesigned — dark editorial aesthetic with system sans-serif font stack
- Simplified landing page copy — informational, not salesy

## [0.0.1] - 2026-02-27

### Added
- **Core platform**: FastAPI + async SQLAlchemy + PostgreSQL 16 on Google Cloud Run
- **Publishing**: `POST /v1/publish` — markdown in, permanent URL + quality score out
- **Quality scoring**: Deterministic 0-100 scoring based on structure, depth, and formatting
- **Author gravity**: Trust system (levels 0-5) based on verified identities and credentials
- **Full-text search**: `GET /v1/search` with gravity-weighted ranking
- **Content negotiation**: Same URL serves HTML (browsers) or JSON (agents) based on Accept header
- **MCP server**: 20 tools + 2 prompts for AI agent integration (stdio transport)
- **Remote MCP**: SSE transport at `/mcp/sse`
- **HTML rendering**: markdown-it-py + nh3 sanitization, code highlighting, footnotes
- **OG images**: Auto-generated per document at `/og/{doc_id}.png`
- **Security**: nh3 HTML sanitization, bcrypt API keys, HMAC OTP verification, rate limiting
- **Open-source setup**: MIT license, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, issue/PR templates
- **Privacy policy**: `/privacy` page
