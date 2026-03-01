"""lightpaper.org — API-first publishing platform."""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

MAX_BODY_SIZE = 2 * 1024 * 1024  # 2 MB

app = FastAPI(
    title="lightpaper.org",
    description="API-first publishing platform. One HTTP call, one permanent URL.",
    version="0.1.0",
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
)


# --- Security headers middleware ---

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    DOCS_PATHS = {"/v1/docs", "/v1/openapi.json", "/v1/redoc"}

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if request.url.path in self.DOCS_PATHS:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' https: data:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "frame-ancestors 'none'"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'none'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' https:; frame-ancestors 'none'"
            )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# --- Request body size limit middleware ---

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large. Maximum size is {MAX_BODY_SIZE // (1024 * 1024)}MB."},
            )
        return await call_next(request)


app.add_middleware(BodySizeLimitMiddleware)


# --- CORS middleware ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# --- Rate limiting ---

from slowapi.errors import RateLimitExceeded

from app.rate_limit import limiter

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "lightpaper", "version": "0.1.0"}


def mount_routes():
    """Mount all routers. Called after all route modules are defined."""
    from app.routes import publish, documents, search, accounts, keys, verification, discovery, landing, reading, onboard, linkedin, credentials, author

    app.include_router(publish.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    app.include_router(accounts.router)
    app.include_router(keys.router)
    app.include_router(verification.router)
    app.include_router(onboard.router)
    app.include_router(linkedin.router)
    app.include_router(credentials.router)
    app.include_router(discovery.router)
    app.include_router(landing.router)
    # Author profiles before catch-all
    app.include_router(author.router)
    # Reading routes LAST — catch-all /{slug}
    app.include_router(reading.router)


mount_routes()
