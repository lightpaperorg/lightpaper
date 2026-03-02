"""lightpaper.org MCP server — 16 tools + prompts, stdio transport."""

import os

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import GetPromptResult, PromptArgument, PromptMessage, TextContent, Tool

BASE_URL = os.getenv("LIGHTPAPER_BASE_URL", "https://lightpaper.org")
API_KEY = os.getenv("LIGHTPAPER_API_KEY", "")

SERVER_INSTRUCTIONS = """\
You are an agent that publishes and manages documents on lightpaper.org — an API-first publishing platform.

## How authentication works

- If LIGHTPAPER_API_KEY is set in the environment, all tools use it automatically.
- If no API key is configured, you need to sign in or create an account first:
  1. Ask the user for their name, email, and preferred handle
  2. Call auth_email to send a verification code to their email
  3. Ask the user for the 6-digit code from their email
  4. Call auth_verify with the session_id and code → returns an api_key
  5. Use the api_key in all subsequent tool calls via the api_key parameter
- This flow works for both new signups AND existing accounts (login).
- Store the api_key for the duration of the conversation. Do not ask the user to manage keys.
- Alternative: auth_linkedin starts a browser-based LinkedIn OAuth flow. Poll with auth_linkedin_poll.

## Typical flows

**"Write a post about X"** (most common):
1. If no API key → ask user for name/email/handle → auth_email → ask for code → auth_verify → save the returned api_key
2. Write the article as markdown (300+ words, at least one # heading)
3. Pick the best format: 'markdown' (blog), 'academic' (research), 'report' (business), 'tutorial' (how-to)
4. Call publish_lightpaper with title, content, format, and authors (use the user's name + handle)
5. Share the returned URL with the user
6. If quality_score < 60, review the suggestions and offer to improve the article

**"Find articles about X"**:
1. Call search_lightpapers with the query

**"Delete my article"**:
1. Call list_my_lightpapers to find the document ID
2. Confirm with the user, then call delete_lightpaper

**Boost author gravity (verification)**:
1. Check current level: get_gravity_info → shows level, badges, and next_level instructions
2. Domain: verify_domain (set DNS TXT record, then check) — fully automatable if user has DNS access
3. LinkedIn: verify_linkedin action='start' → give user the OAuth URL → poll with action='check'
4. ORCID: verify_orcid with their ORCID iD — fully automatable
5. Credentials: verify_credentials with degrees/certs/employment — ask user for details

## Quality tips for writing

To score well (60+), articles should have:
- Multiple headings (h2/h3) for structure (up to 20 pts)
- 500+ words of substance (up to 25 pts)
- Varied paragraph lengths, not walls of text (up to 20 pts)
- Lists, code blocks, or blockquotes for variety
- No clickbait or ALL CAPS titles
- Citations or links to sources (up to 15 pts)

## Important notes

- Content must be markdown. Minimum 300 words with at least one heading.
- The platform auto-generates a quality score (0-100) and a permanent URL.
- Authors can include multiple people with name + handle.
- Always tell the user the URL of their published article.
"""

server = Server("lightpaper", instructions=SERVER_INSTRUCTIONS)

API_KEY_PARAM = {
    "api_key": {
        "type": "string",
        "description": "API key to authenticate as a specific account. Overrides the default LIGHTPAPER_API_KEY. Use the key returned by onboard_pilot to act on behalf of that account.",
    },
}


def _headers(api_key: str | None = None) -> dict:
    key = api_key or API_KEY
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _json_headers(api_key: str | None = None) -> dict:
    """Headers for endpoints that use content negotiation (Accept: application/json)."""
    h = _headers(api_key)
    h["Accept"] = "application/json"
    return h


@server.list_prompts()
async def list_prompts():
    return [
        {
            "name": "write-article",
            "description": "Write and publish an article on lightpaper.org. Guides you through the full flow.",
            "arguments": [
                PromptArgument(name="topic", description="What to write about", required=True),
                PromptArgument(name="format", description="markdown, academic, report, or tutorial", required=False),
            ],
        },
        {
            "name": "setup-account",
            "description": "Create a lightpaper.org account and optionally verify identity for higher gravity.",
            "arguments": [],
        },
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
    if name == "write-article":
        topic = (arguments or {}).get("topic", "a topic of your choice")
        fmt = (arguments or {}).get("format", "")
        fmt_hint = f" Use the '{fmt}' format." if fmt else ""
        return GetPromptResult(
            description=f"Write and publish an article about: {topic}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"Write an article about: {topic}\n\n"
                            f"Publish it on lightpaper.org using the publish_lightpaper tool.{fmt_hint}\n\n"
                            "Requirements:\n"
                            "- At least 300 words of real, substantive content\n"
                            "- Use markdown with headings (## Section), paragraphs, and at least one list or code block\n"
                            "- Include a compelling title and subtitle\n"
                            "- If I don't have an account yet, ask for my name, email, and preferred @handle, then use auth_email + auth_verify\n"
                            "- After publishing, share the URL with me\n"
                            "- If the quality score is below 60, offer to improve it"
                        ),
                    ),
                )
            ],
        )
    elif name == "setup-account":
        return GetPromptResult(
            description="Set up a lightpaper.org account with identity verification",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            "Help me set up my lightpaper.org author account.\n\n"
                            "1. Ask for my name, email, and preferred @handle, then sign in with auth_email + auth_verify\n"
                            "2. After account creation, check my gravity level and explain what it means\n"
                            "3. Walk me through verification options to increase my gravity:\n"
                            "   - Domain verification (if I own a website)\n"
                            "   - LinkedIn verification\n"
                            "   - ORCID verification (if I'm a researcher)\n"
                            "   - Academic/professional credentials\n"
                            "4. Let me choose which verifications to do and guide me through each one"
                        ),
                    ),
                )
            ],
        )
    raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="publish_lightpaper",
            description=(
                "Publish a document to lightpaper.org. Returns a permanent URL, quality score (0-100), "
                "and quality suggestions. Content must be markdown with at least 300 words and one heading."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title (max 500 chars)"},
                    "content": {
                        "type": "string",
                        "description": "Markdown content (min 300 words, must include at least one # heading)",
                    },
                    "subtitle": {"type": "string", "description": "Optional subtitle (max 1000 chars)"},
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "academic", "report", "tutorial"],
                        "default": "markdown",
                        "description": (
                            "Presentation format. 'markdown': default blog style. "
                            "'academic': use for research papers, literature reviews — serif font, auto-numbered h2 headings, first blockquote renders as Abstract callout. "
                            "'report': use for business/technical reports — wider layout, inverted table headers, first blockquote renders as Executive Summary callout. "
                            "'tutorial': use for how-to guides, walkthroughs — h2 headings auto-prefixed 'Step N:', prominent code blocks, blockquotes styled as tip callouts."
                        ),
                    },
                    "authors": {
                        "type": "array",
                        "maxItems": 20,
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Author display name"},
                                "handle": {
                                    "type": "string",
                                    "description": "Author handle (links to /@handle profile)",
                                },
                            },
                            "required": ["name"],
                        },
                        "description": "Author attribution. If omitted, the publishing account is not credited by name.",
                    },
                    "slug": {
                        "type": "string",
                        "description": "Custom URL slug (max 80 chars). Auto-generated from title if omitted.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for search filtering (max 50)",
                    },
                    "listed": {
                        "type": "boolean",
                        "default": True,
                        "description": "If true, document appears in search results and sitemap.",
                    },
                    **API_KEY_PARAM,
                },
                "required": ["title", "content"],
            },
        ),
        Tool(
            name="search_lightpapers",
            description="Search published documents on lightpaper.org. Returns titles, URLs, authors, quality scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Full-text search query"},
                    "author": {"type": "string", "description": "Filter by author handle (e.g. 'alice')"},
                    "tags": {"type": "string", "description": "Comma-separated tag filter (e.g. 'python,ml')"},
                    "min_quality": {
                        "type": "integer",
                        "default": 40,
                        "description": "Minimum quality score 0-100 (default 40)",
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["relevance", "recent", "quality"],
                        "default": "relevance",
                        "description": "Sort order",
                    },
                    "limit": {"type": "integer", "default": 20, "description": "Results per page (1-100)"},
                    "offset": {"type": "integer", "default": 0, "description": "Pagination offset"},
                    **API_KEY_PARAM,
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_lightpaper",
            description="Get a document by ID from lightpaper.org. Returns full content, metadata, quality score, and author info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Document ID (doc_xxxx)"},
                    **API_KEY_PARAM,
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="update_lightpaper",
            description=(
                "Update an existing document. Only the document owner can update. "
                "Content updates create a new version (max 100 versions). Quality score is recalculated on content change."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Document ID"},
                    "title": {"type": "string", "description": "New title"},
                    "subtitle": {"type": "string", "description": "New subtitle"},
                    "content": {"type": "string", "description": "New markdown content (creates a new version)"},
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "handle": {"type": "string"},
                            },
                            "required": ["name"],
                        },
                        "description": "Replace author list",
                    },
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Replace tags"},
                    "listed": {
                        "type": "boolean",
                        "description": "Set to false to remove from search results and sitemap",
                    },
                    "metadata": {"type": "object", "description": "Replace custom metadata"},
                    **API_KEY_PARAM,
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="delete_lightpaper",
            description="Delete a document (soft-delete). Only the document owner can delete. Returns 204 on success.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Document ID to delete"},
                    **API_KEY_PARAM,
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="list_my_lightpapers",
            description="List all documents published by the authenticated account. Returns id, title, slug, quality_score, listed status, URLs, and timestamps.",
            inputSchema={
                "type": "object",
                "properties": {
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="get_account_info",
            description="Get the authenticated account's info: handle, display name, email, gravity level, verification badges, and tier.",
            inputSchema={
                "type": "object",
                "properties": {
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="get_gravity_info",
            description=(
                "Get the authenticated account's gravity level details: current level (0-5), search ranking multiplier, "
                "featured quality threshold, verification badges, and instructions for reaching the next level."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="get_author_profile",
            description="Get a public author profile by handle. Returns display name, bio, gravity level, badges, and their published documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Author handle (without @)"},
                },
                "required": ["handle"],
            },
        ),
        Tool(
            name="get_document_versions",
            description="List version history for a document. Each version has a content hash, word count, reading time, and timestamp.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Document ID"},
                    **API_KEY_PARAM,
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="list_credentials",
            description="List all verified credentials submitted for the authenticated account.",
            inputSchema={
                "type": "object",
                "properties": {
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="auth_email",
            description=(
                "Send a 6-digit verification code to the user's email. Works for both signup and login. "
                "After calling this, ask the user for the code and call auth_verify."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email address"},
                    "display_name": {"type": "string", "description": "User's display name (for new accounts)"},
                    "handle": {
                        "type": "string",
                        "description": "Unique handle (e.g. 'alice'). Used in author profiles at /@handle.",
                    },
                },
                "required": ["email"],
            },
        ),
        Tool(
            name="auth_verify",
            description=(
                "Verify a 6-digit code from the user's email. Returns account info and an API key. "
                "Use the returned api_key in all subsequent tool calls."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID returned by auth_email",
                    },
                    "code": {
                        "type": "string",
                        "description": "6-digit code from the user's email",
                    },
                },
                "required": ["session_id", "code"],
            },
        ),
        Tool(
            name="auth_linkedin",
            description=(
                "Start LinkedIn OAuth for login/signup. Returns an authorization URL for the user to open "
                "in their browser, and a session_id for polling. After the user completes OAuth, call auth_linkedin_poll."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="auth_linkedin_poll",
            description=(
                "Poll for LinkedIn OAuth completion. Returns the API key once the user completes the OAuth flow. "
                "The API key is only returned on the first poll — subsequent polls return null."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID returned by auth_linkedin",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="verify_domain",
            description="Start or check domain DNS verification. Call with domain to start (returns TXT record to add), call without to check status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to verify (omit to check existing verification)",
                    },
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="verify_linkedin",
            description="Start or check LinkedIn verification. Call with action='start' to get OAuth URL (user must open in browser), action='check' to poll completion.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start", "check"],
                        "description": "'start' to begin OAuth, 'check' to poll completion",
                    },
                    **API_KEY_PARAM,
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="verify_orcid",
            description="Verify an ORCID iD. Validates against the public ORCID API. Fully automatable — no browser needed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "orcid_id": {"type": "string", "description": "ORCID iD (e.g. 0000-0002-1825-0097)"},
                    **API_KEY_PARAM,
                },
                "required": ["orcid_id"],
            },
        ),
        Tool(
            name="verify_credentials",
            description=(
                "Submit verified credentials (degrees, certifications, employment) for an account. "
                "Evidence tiers: 'confirmed' (3pts, institutional API match), 'supported' (2pts, corroborating evidence), "
                "'claimed' (1pt, user's word). Reaching 3+ points with level 3 base grants level 4; 6+ points grants level 5. "
                "Tiers can only be upgraded, never downgraded on re-submit."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "credentials": {
                        "type": "array",
                        "maxItems": 20,
                        "items": {
                            "type": "object",
                            "properties": {
                                "credential_type": {
                                    "type": "string",
                                    "enum": ["degree", "certification", "employment"],
                                },
                                "institution": {
                                    "type": "string",
                                    "description": "Institution name (e.g. 'Curtin University')",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Credential title (e.g. 'Bachelor of Science in Computer Science')",
                                },
                                "year": {"type": "integer", "description": "Year awarded/completed"},
                                "evidence_tier": {"type": "string", "enum": ["confirmed", "supported", "claimed"]},
                                "evidence_data": {
                                    "type": "object",
                                    "description": "API responses, URLs, or other verification data",
                                },
                                "agent_notes": {"type": "string", "description": "How you verified this credential"},
                            },
                            "required": ["credential_type", "institution", "title", "evidence_tier"],
                        },
                    },
                    **API_KEY_PARAM,
                },
                "required": ["credentials"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Extract api_key before passing arguments to endpoints
    api_key = arguments.pop("api_key", None)
    headers = _headers(api_key)

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        if name == "publish_lightpaper":
            payload = {
                "title": arguments["title"],
                "content": arguments["content"],
                "metadata": {},
                "options": {"listed": arguments.get("listed", True)},
            }
            if arguments.get("format"):
                payload["format"] = arguments["format"]
            if arguments.get("subtitle"):
                payload["subtitle"] = arguments["subtitle"]
            if arguments.get("authors"):
                payload["authors"] = arguments["authors"]
            if arguments.get("slug"):
                payload["options"]["slug"] = arguments["slug"]
            if arguments.get("tags"):
                payload["metadata"]["tags"] = arguments["tags"]

            resp = await client.post("/v1/publish", json=payload)
            return [TextContent(type="text", text=resp.text)]

        elif name == "search_lightpapers":
            params = {"q": arguments["query"], "limit": arguments.get("limit", 20)}
            if arguments.get("author"):
                params["author"] = arguments["author"]
            if arguments.get("tags"):
                params["tags"] = arguments["tags"]
            if arguments.get("min_quality") is not None:
                params["min_quality"] = arguments["min_quality"]
            if arguments.get("sort"):
                params["sort"] = arguments["sort"]
            if arguments.get("offset"):
                params["offset"] = arguments["offset"]
            resp = await client.get("/v1/search", params=params)
            return [TextContent(type="text", text=resp.text)]

        elif name == "get_lightpaper":
            resp = await client.get(f"/v1/documents/{arguments['id']}")
            return [TextContent(type="text", text=resp.text)]

        elif name == "update_lightpaper":
            doc_id = arguments.pop("id")
            payload = {k: v for k, v in arguments.items() if v is not None}
            resp = await client.put(f"/v1/documents/{doc_id}", json=payload)
            return [TextContent(type="text", text=resp.text)]

        elif name == "delete_lightpaper":
            resp = await client.delete(f"/v1/documents/{arguments['id']}")
            if resp.status_code == 204:
                return [TextContent(type="text", text='{"deleted": true}')]
            return [TextContent(type="text", text=resp.text)]

        elif name == "list_my_lightpapers":
            resp = await client.get("/v1/account/documents")
            return [TextContent(type="text", text=resp.text)]

        elif name == "get_account_info":
            resp = await client.get("/v1/account")
            return [TextContent(type="text", text=resp.text)]

        elif name == "get_gravity_info":
            resp = await client.get("/v1/account/gravity")
            return [TextContent(type="text", text=resp.text)]

        elif name == "get_author_profile":
            handle = arguments["handle"]
            json_headers = _json_headers(api_key)
            resp = await client.get(f"/@{handle}", headers=json_headers)
            return [TextContent(type="text", text=resp.text)]

        elif name == "get_document_versions":
            resp = await client.get(f"/v1/documents/{arguments['id']}/versions")
            return [TextContent(type="text", text=resp.text)]

        elif name == "list_credentials":
            resp = await client.get("/v1/account/credentials")
            return [TextContent(type="text", text=resp.text)]

        elif name == "auth_email":
            payload = {"email": arguments["email"]}
            if arguments.get("display_name"):
                payload["display_name"] = arguments["display_name"]
            if arguments.get("handle"):
                payload["handle"] = arguments["handle"]
            resp = await client.post("/v1/auth/email", json=payload)
            return [TextContent(type="text", text=resp.text)]

        elif name == "auth_verify":
            payload = {
                "session_id": arguments["session_id"],
                "code": arguments["code"],
            }
            resp = await client.post("/v1/auth/verify", json=payload)
            return [TextContent(type="text", text=resp.text)]

        elif name == "auth_linkedin":
            resp = await client.post("/v1/auth/linkedin")
            return [TextContent(type="text", text=resp.text)]

        elif name == "auth_linkedin_poll":
            resp = await client.get(
                "/v1/auth/linkedin/poll",
                params={"session_id": arguments["session_id"]},
            )
            return [TextContent(type="text", text=resp.text)]

        elif name == "verify_domain":
            if arguments.get("domain"):
                resp = await client.post(
                    "/v1/account/verify/domain",
                    json={"domain": arguments["domain"]},
                )
            else:
                resp = await client.get("/v1/account/verify/domain/check")
            return [TextContent(type="text", text=resp.text)]

        elif name == "verify_linkedin":
            action = arguments["action"]
            if action == "start":
                resp = await client.post("/v1/account/verify/linkedin")
            else:
                resp = await client.get("/v1/account/verify/linkedin/check")
            return [TextContent(type="text", text=resp.text)]

        elif name == "verify_orcid":
            resp = await client.post(
                "/v1/account/verify/orcid",
                json={"orcid_id": arguments["orcid_id"]},
            )
            return [TextContent(type="text", text=resp.text)]

        elif name == "verify_credentials":
            payload = {"credentials": arguments["credentials"]}
            resp = await client.post("/v1/account/credentials", json=payload)
            return [TextContent(type="text", text=resp.text)]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
