"""Remote MCP endpoint via SSE transport.

Provides two ASGI apps mounted as Starlette routes:
- GET  /mcp/sse          — SSE stream (sends endpoint event, then streams messages)
- POST /mcp/messages/    — Client posts JSONRPC messages with ?session_id=xxx

Uses the same MCP server instance as the stdio transport (mcp/server.py).
No auth on SSE connection — individual tools use per-call `api_key` param.
"""

import logging
import sys

from starlette.requests import Request
from starlette.routing import Mount, Route

logger = logging.getLogger(__name__)


def create_mcp_routes() -> list[Route | Mount]:
    """Create Starlette routes for MCP SSE transport.

    Imports are done inside the function to avoid circular imports
    (mcp/server.py shadows the mcp package when imported from the project root).
    """
    # Add parent directory to sys.path so we can import mcp/server.py as mcp_server
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # Import the MCP server object — must use importlib to avoid shadowing
    import importlib.util

    spec = importlib.util.spec_from_file_location("mcp_app_server", os.path.join(project_root, "mcp", "server.py"))
    mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_module)
    mcp_server = mcp_module.server

    from mcp.server.sse import SseServerTransport

    sse_transport = SseServerTransport("/mcp/messages/")

    async def handle_sse(request: Request):
        logger.info("MCP SSE connection established")
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

    return [
        Route("/mcp/sse", endpoint=handle_sse),
        Mount("/mcp/messages/", app=sse_transport.handle_post_message),
    ]
