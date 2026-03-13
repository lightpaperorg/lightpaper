"""Narration routes: estimate, create, status, callback, voices."""

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthResult, require_account
from app.config import settings
from app.database import get_db
from app.models import Account, Book, Narration, NarrationChapter
from app.rate_limit import limiter
from app.schemas import NarrationCreateRequest, NarrationEstimateRequest, NarrationEstimateResponse, NarrationResponse, NarrationChapterResponse
from app.services.narration import (
    VOICES,
    estimate_narration,
    generate_callback_token,
    generate_narration_id,
    handle_callback,
    start_narration,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/narration", tags=["narration"])


def _require_pro(account: Account):
    if (account.tier or "free") != "pro":
        raise HTTPException(status_code=403, detail="Narration requires a Pro subscription")


def _init_stripe():
    if not settings.stripe_api_key:
        raise HTTPException(status_code=503, detail="Billing not configured")
    stripe.api_key = settings.stripe_api_key


@router.get("/voices")
@limiter.limit("60/minute")
async def list_voices(request: Request):
    """List available narration voices."""
    return {"voices": VOICES}


@router.post("/estimate")
@limiter.limit("30/minute")
async def narration_estimate(
    request: Request,
    body: NarrationEstimateRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Estimate narration cost for a book."""
    _require_pro(auth.account)

    try:
        estimate = await estimate_narration(body.book_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return NarrationEstimateResponse(**estimate)


@router.post("/create")
@limiter.limit("10/hour")
async def create_narration(
    request: Request,
    body: NarrationCreateRequest,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Create a narration and return a Stripe checkout URL for payment."""
    _require_pro(auth.account)
    _init_stripe()

    account = auth.account

    # Verify book ownership
    book_result = await db.execute(
        select(Book).where(Book.id == body.book_id, Book.account_id == account.id, Book.deleted_at.is_(None))
    )
    book = book_result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found or not owned by you")

    # Check no active narration exists for this book
    existing = await db.execute(
        select(Narration).where(
            Narration.book_id == body.book_id,
            Narration.status.in_(["pending", "paid", "processing", "converting"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An active narration already exists for this book")

    # Validate voice
    valid_voices = {v["voice_id"] for v in VOICES}
    if body.voice_id not in valid_voices:
        raise HTTPException(status_code=400, detail="Invalid voice_id. Use GET /v1/narration/voices for options.")

    voice_name = next(v["name"] for v in VOICES if v["voice_id"] == body.voice_id)

    # Get estimate for pricing
    try:
        estimate = await estimate_narration(body.book_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    narration_id = generate_narration_id()
    callback_token = generate_callback_token()

    # Create narration record
    narration = Narration(
        id=narration_id,
        book_id=body.book_id,
        account_id=account.id,
        voice_id=body.voice_id,
        voice_name=voice_name,
        status="pending",
        total_characters=estimate["total_characters"],
        price_cents=estimate["price_cents"],
        callback_token=callback_token,
    )
    db.add(narration)

    # Create chapter records
    for ch_est in estimate["chapters"]:
        ch = NarrationChapter(
            narration_id=narration_id,
            document_id=ch_est["document_id"],
            chapter_number=ch_est["chapter_number"],
            character_count=ch_est["character_count"],
        )
        db.add(ch)

    await db.flush()

    # Get or create Stripe customer
    customer_id = account.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=account.email,
            name=account.display_name or account.handle,
            metadata={"lightpaper_account_id": str(account.id)},
        )
        customer_id = customer.id
        await db.execute(
            update(Account).where(Account.id == account.id).values(stripe_customer_id=customer_id)
        )

    # Create Stripe Checkout for one-time payment
    base_url = settings.base_url
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": estimate["price_cents"],
                "product_data": {
                    "name": f"Audiobook Narration: {book.title}",
                    "description": f"{len(estimate['chapters'])} chapters, {estimate['total_characters']:,} characters, voice: {voice_name}",
                },
            },
            "quantity": 1,
        }],
        success_url=f"{base_url}/write?narration=success&narration_id={narration_id}",
        cancel_url=f"{base_url}/write?narration=cancelled",
        metadata={
            "lightpaper_account_id": str(account.id),
            "narration_id": narration_id,
        },
    )

    narration.stripe_checkout_session_id = checkout_session.id
    await db.commit()

    return {
        "narration_id": narration_id,
        "checkout_url": checkout_session.url,
        "price_display": estimate["price_display"],
    }


@router.get("/{narration_id}")
@limiter.limit("60/minute")
async def get_narration_status(
    narration_id: str,
    request: Request,
    auth: AuthResult = Depends(require_account),
    db: AsyncSession = Depends(get_db),
):
    """Get narration status and chapter audio URLs."""
    narration_result = await db.execute(
        select(Narration).where(Narration.id == narration_id, Narration.account_id == auth.account.id)
    )
    narration = narration_result.scalar_one_or_none()
    if not narration:
        raise HTTPException(status_code=404, detail="Narration not found")

    chapters_result = await db.execute(
        select(NarrationChapter).where(NarrationChapter.narration_id == narration_id)
        .order_by(NarrationChapter.chapter_number)
    )
    chapters = chapters_result.scalars().all()

    return NarrationResponse(
        id=narration.id,
        book_id=narration.book_id,
        voice_id=narration.voice_id,
        voice_name=narration.voice_name,
        status=narration.status,
        error_message=narration.error_message,
        total_characters=narration.total_characters,
        price_cents=narration.price_cents,
        price_display=f"${narration.price_cents / 100:.2f}",
        audio_ready=narration.audio_ready,
        created_at=narration.created_at,
        completed_at=narration.completed_at,
        chapters=[
            NarrationChapterResponse(
                chapter_number=ch.chapter_number,
                document_id=ch.document_id,
                character_count=ch.character_count,
                audio_url=ch.audio_url,
                audio_duration_seconds=ch.audio_duration_seconds,
                status=ch.status,
            )
            for ch in chapters
        ],
    )


@router.post("/callback/{callback_token}")
async def narration_callback(
    callback_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """ElevenLabs completion callback — no auth, token IS the auth."""
    success = await handle_callback(callback_token, db)
    if not success:
        return Response(status_code=404)
    return Response(status_code=200)
