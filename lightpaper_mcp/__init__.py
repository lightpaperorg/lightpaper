"""lightpaper-mcp — MCP server for lightpaper.org publishing platform."""

from lightpaper_mcp.server import main, server

__all__ = ["server", "main"]


def run():
    """Entry point for `lightpaper-mcp` CLI command."""
    import asyncio

    asyncio.run(main())
