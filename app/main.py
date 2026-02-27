"""lightpaper.org — API-first publishing platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings

app = FastAPI(
    title="lightpaper.org",
    description="API-first publishing platform. One HTTP call, one permanent URL.",
    version="0.1.0",
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "lightpaper", "version": "0.1.0"}


def mount_routes():
    """Mount all routers. Called after all route modules are defined."""
    from app.routes import publish, documents, search, accounts, keys, verification, discovery, landing, reading

    app.include_router(publish.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    app.include_router(accounts.router)
    app.include_router(keys.router)
    app.include_router(verification.router)
    app.include_router(discovery.router)
    app.include_router(landing.router)
    # Reading routes LAST — catch-all /{slug}
    app.include_router(reading.router)


mount_routes()
