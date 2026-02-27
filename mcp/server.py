"""lightpaper.org MCP server — 9 tools, stdio transport."""

import json
import os

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

BASE_URL = os.getenv("LIGHTPAPER_BASE_URL", "https://lightpaper.org")
API_KEY = os.getenv("LIGHTPAPER_API_KEY", "")

server = Server("lightpaper")

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


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="publish_lightpaper",
            description="Publish a document to lightpaper.org. Returns a permanent URL and quality score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "content": {"type": "string", "description": "Markdown content (min 300 words)"},
                    "subtitle": {"type": "string", "description": "Optional subtitle"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
                    "listed": {"type": "boolean", "default": True, "description": "Whether to list in search"},
                    **API_KEY_PARAM,
                },
                "required": ["title", "content"],
            },
        ),
        Tool(
            name="search_lightpapers",
            description="Search published documents on lightpaper.org.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "tags": {"type": "string", "description": "Comma-separated tags"},
                    "limit": {"type": "integer", "default": 10},
                    **API_KEY_PARAM,
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_lightpaper",
            description="Get a document by ID from lightpaper.org.",
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
            description="Update an existing document on lightpaper.org.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Document ID"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    **API_KEY_PARAM,
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="list_my_lightpapers",
            description="List all documents published by the authenticated account.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="onboard_pilot",
            description="Create a lightpaper account for a pilot (human user). Returns an API key. No browser needed. Use the returned api_key in subsequent calls to act as that account.",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Pilot's email address"},
                    "display_name": {"type": "string", "description": "Pilot's display name"},
                    "handle": {"type": "string", "description": "Unique handle (e.g. 'alice')"},
                },
                "required": ["email"],
            },
        ),
        Tool(
            name="verify_domain",
            description="Start or check domain DNS verification. Call with domain to start, call without to check status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain to verify (omit to check existing verification)"},
                    **API_KEY_PARAM,
                },
            },
        ),
        Tool(
            name="verify_linkedin",
            description="Start or check LinkedIn verification. Call with action='start' to get OAuth URL, action='check' to poll status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["start", "check"], "description": "'start' to begin OAuth, 'check' to poll completion"},
                    **API_KEY_PARAM,
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="verify_orcid",
            description="Verify an ORCID iD. Validates against the public ORCID API. Fully automatable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "orcid_id": {"type": "string", "description": "ORCID iD (e.g. 0000-0002-1825-0097)"},
                    **API_KEY_PARAM,
                },
                "required": ["orcid_id"],
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
            if arguments.get("subtitle"):
                payload["subtitle"] = arguments["subtitle"]
            if arguments.get("tags"):
                payload["metadata"]["tags"] = arguments["tags"]

            resp = await client.post("/v1/publish", json=payload)
            return [TextContent(type="text", text=resp.text)]

        elif name == "search_lightpapers":
            params = {"q": arguments["query"], "limit": arguments.get("limit", 10)}
            if arguments.get("tags"):
                params["tags"] = arguments["tags"]
            resp = await client.get("/v1/search", params=params)
            return [TextContent(type="text", text=resp.text)]

        elif name == "get_lightpaper":
            resp = await client.get(
                f"/v1/documents/{arguments['id']}",
            )
            return [TextContent(type="text", text=resp.text)]

        elif name == "update_lightpaper":
            doc_id = arguments.pop("id")
            payload = {k: v for k, v in arguments.items() if v is not None}
            resp = await client.put(f"/v1/documents/{doc_id}", json=payload)
            return [TextContent(type="text", text=resp.text)]

        elif name == "list_my_lightpapers":
            params = {"limit": arguments.get("limit", 20)}
            resp = await client.get("/v1/account/documents", params=params)
            return [TextContent(type="text", text=resp.text)]

        elif name == "onboard_pilot":
            payload = {"email": arguments["email"]}
            if arguments.get("display_name"):
                payload["display_name"] = arguments["display_name"]
            if arguments.get("handle"):
                payload["handle"] = arguments["handle"]
            resp = await client.post("/v1/onboard", json=payload)
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

        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
