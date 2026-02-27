"""Shared utilities for lightpaper.org."""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Extract the real client IP from X-Forwarded-For (set by Cloud Run proxy).

    Cloud Run (and most reverse proxies) append the client IP as the first
    entry in X-Forwarded-For. request.client.host returns the proxy IP, which
    means all anonymous requests share one rate-limit bucket without this.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First IP in the chain is the real client
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
