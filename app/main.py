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
    INLINE_SCRIPT_PATHS = {"/"}

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
        elif request.url.path in self.INLINE_SCRIPT_PATHS:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' https:; frame-ancestors 'none'"
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


@app.get("/health/ready")
async def health_ready():
    """Readiness check — verifies database connectivity."""
    from sqlalchemy import text

    from app.database import engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"
    return {"status": status, "service": "lightpaper", "version": "0.1.0", "database": db_status}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    import os

    from fastapi.responses import FileResponse

    return FileResponse(
        os.path.join(os.path.dirname(__file__), "static", "favicon.ico"),
        media_type="image/x-icon",
        headers={"Cache-Control": "public, max-age=604800"},
    )


def mount_static():
    """Mount static files (favicon, icons, fonts)."""
    import os

    from fastapi.staticfiles import StaticFiles

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


mount_static()


def mount_routes():
    """Mount all routers. Called after all route modules are defined."""
    from app.routes import (
        accounts,
        auth,
        author,
        credentials,
        discovery,
        documents,
        keys,
        landing,
        linkedin,
        publish,
        reading,
        search,
        verification,
    )

    app.include_router(publish.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    app.include_router(accounts.router)
    app.include_router(keys.router)
    app.include_router(verification.router)
    app.include_router(auth.router)
    app.include_router(linkedin.router)
    app.include_router(credentials.router)
    app.include_router(discovery.router)
    app.include_router(landing.router)
    # Author profiles before catch-all
    app.include_router(author.router)
    # Reading routes LAST — catch-all /{slug}
    app.include_router(reading.router)


mount_routes()


@app.on_event("startup")
async def run_migrations():
    """Apply pending migrations on startup (idempotent)."""
    import logging
    import os

    from sqlalchemy import text

    from app.database import engine

    migration_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")
    if not os.path.isdir(migration_dir):
        return

    logger = logging.getLogger("lightpaper.migrations")
    for filename in sorted(os.listdir(migration_dir)):
        if not filename.endswith(".sql"):
            continue
        filepath = os.path.join(migration_dir, filename)
        sql = open(filepath).read()
        # Execute each statement in its own transaction (idempotent — skip on error)
        for statement in sql.split(";"):
            statement = statement.strip()
            # Skip empty lines and pure comments
            if not statement or all(
                line.strip().startswith("--") or not line.strip()
                for line in statement.split("\n")
            ):
                continue
            try:
                async with engine.begin() as conn:
                    await conn.execute(text(statement))
            except Exception as e:
                logger.warning("Migration %s: skipped statement: %s", filename, str(e)[:200])
        logger.info("Migration completed: %s", filename)
