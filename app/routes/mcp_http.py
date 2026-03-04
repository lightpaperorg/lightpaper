"""Remote MCP endpoint via Streamable HTTP transport.

Single endpoint at /mcp handles:
- POST  — JSON-RPC requests (initialize, tool calls, etc.)
- GET   — Optional SSE stream for server-initiated notifications
- DELETE — Session termination

Uses the same MCP server instance as the stdio transport (mcp/server.py).
No auth on the HTTP connection — individual tools use per-call `api_key` param.
"""

import logging

from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

# Module-level reference so lifespan can manage it
_session_manager = None


def create_mcp_routes() -> list[Mount]:
    """Create Starlette routes for MCP Streamable HTTP transport.

    Imports are done inside the function to avoid circular imports
    (mcp/server.py shadows the mcp package when imported from the project root).
    """
    import importlib.util
    import os

    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

    global _session_manager

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # Import the MCP server object — must use importlib to avoid shadowing
    spec = importlib.util.spec_from_file_location("mcp_app_server", os.path.join(project_root, "mcp", "server.py"))
    mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_module)
    mcp_server = mcp_module.server

    _session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        json_response=False,
    )

    async def handle_mcp(scope: Scope, receive: Receive, send: Send) -> None:
        await _session_manager.handle_request(scope, receive, send)

    return [
        Mount("/mcp", app=handle_mcp),
    ]
