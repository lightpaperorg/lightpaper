"""IDE routes: serves the React SPA for the Writing IDE."""

import os

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

router = APIRouter(tags=["ide"])

IDE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ide", "dist")

_index_cache: str | None = None


def _spa_index() -> str | None:
    """Read the SPA index.html if it exists (built by Vite)."""
    global _index_cache
    if _index_cache is not None:
        return _index_cache
    index_path = os.path.join(IDE_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path) as f:
            _index_cache = f.read()
        return _index_cache
    return None


@router.get("/write/{path:path}")
@router.get("/write")
async def ide_spa(request: Request, path: str = "") -> Response:
    """Serve the React SPA. All /write/* routes return index.html for client-side routing."""
    # Serve static assets from the build (JS, CSS, images)
    if path:
        asset_path = os.path.join(IDE_DIR, path)
        # Prevent directory traversal
        if os.path.commonpath([IDE_DIR, os.path.abspath(asset_path)]) == IDE_DIR:
            if os.path.isfile(asset_path):
                return FileResponse(asset_path)

    html = _spa_index()
    if html:
        return HTMLResponse(html)

    # Dev fallback
    return HTMLResponse(
        """<!DOCTYPE html>
<html>
<head><title>lightpaper — Writing IDE</title></head>
<body style="margin:0; display:flex; align-items:center; justify-content:center; height:100vh; font-family:system-ui; background:#0a0a0a; color:#e0e0e0;">
<div style="text-align:center; max-width:500px;">
<h1 style="font-size:1.5rem;">Writing IDE</h1>
<p style="color:#888;">The React app hasn't been built yet.</p>
<p style="color:#888;">Run <code style="background:#1a1a1a; padding:2px 8px; border-radius:4px;">cd app/ide && npm install && npm run build</code></p>
<p style="color:#888;">Or for development: <code style="background:#1a1a1a; padding:2px 8px; border-radius:4px;">cd app/ide && npm run dev</code></p>
</div>
</body>
</html>""",
        status_code=200,
    )
