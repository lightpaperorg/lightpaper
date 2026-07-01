"""Image hosting: upload endpoints (/v1/assets) + on-domain serving (/i/{key}).

Images referenced in a document render because the reading-page CSP already allows
any https image source; the only missing piece was a place to host them. This is it.
"""

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.database import get_db
from app.rate_limit import limiter
from app.schemas import AssetBase64Request, AssetUploadResponse
from app.services import assets as asset_service

# No prefix: this router owns both /v1/assets (upload) and /i/{key} (serving).
router = APIRouter(tags=["assets"])


def _to_response(ref: asset_service.AssetRef) -> AssetUploadResponse:
    return AssetUploadResponse(
        id=ref.id,
        url=ref.url,
        content_type=ref.content_type,
        bytes=ref.bytes,
        width=ref.width,
        height=ref.height,
    )


@router.post("/v1/assets", response_model=AssetUploadResponse, status_code=201)
@limiter.limit("120/hour")
async def upload_asset(
    request: Request,
    file: UploadFile = File(..., description="Image file (PNG, JPEG, GIF, or WEBP)"),
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image via multipart form-data and get a hosted URL back."""
    data = await file.read()
    try:
        ref = await asset_service.store_asset(db, auth.account.id, data)
    except asset_service.AssetError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    await db.commit()
    return _to_response(ref)


@router.post("/v1/assets/base64", response_model=AssetUploadResponse, status_code=201)
@limiter.limit("120/hour")
async def upload_asset_base64(
    body: AssetBase64Request,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image as base64 JSON (convenient for AI agents) and get a hosted URL back."""
    try:
        data = asset_service.decode_base64_image(body.data)
        ref = await asset_service.store_asset(db, auth.account.id, data)
    except asset_service.AssetError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    await db.commit()
    return _to_response(ref)


@router.get("/i/{key}", include_in_schema=False)
async def serve_asset(key: str):
    """Serve a hosted image. Content-addressed keys are immutable, so cache forever."""
    result = await asset_service.load_asset_bytes(key)
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found")
    data, content_type = result
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
