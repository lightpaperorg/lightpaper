"""Stripe billing: checkout, webhooks, and usage tracking for the Writing IDE."""

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Account, WritingSession
from app.rate_limit import limiter
from app.routes.write import require_ide_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/billing", tags=["billing"])

# Token limits per tier (total per session)
TOKEN_LIMITS = {
    "free": 100_000,      # ~50 pages of writing — enough to try the Wave Method
    "pro": 5_000_000,     # ~2,500 pages — plenty for a full book
    "team": 20_000_000,
}

# Session limits per tier
SESSION_LIMITS = {
    "free": 2,
    "pro": 50,
    "team": 200,
}


def _init_stripe():
    if not settings.stripe_api_key:
        raise HTTPException(status_code=503, detail="Billing not configured")
    stripe.api_key = settings.stripe_api_key


# --- Schemas ---


class CheckoutRequest(BaseModel):
    success_url: str = "/write?billing=success"
    cancel_url: str = "/write?billing=cancelled"


# --- Endpoints ---


@router.get("/status")
async def billing_status(
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Get billing status: tier, usage, limits."""
    # Count active sessions
    result = await db.execute(
        select(WritingSession).where(
            WritingSession.account_id == account.id,
            WritingSession.deleted_at.is_(None),
        )
    )
    sessions = result.scalars().all()
    active_sessions = len(sessions)
    total_tokens = sum(s.total_tokens_used for s in sessions)

    tier = account.tier or "free"
    token_limit = TOKEN_LIMITS.get(tier, TOKEN_LIMITS["free"])
    session_limit = SESSION_LIMITS.get(tier, SESSION_LIMITS["free"])

    return {
        "tier": tier,
        "token_limit": token_limit,
        "tokens_used": total_tokens,
        "tokens_remaining": max(0, token_limit - total_tokens),
        "session_limit": session_limit,
        "active_sessions": active_sessions,
        "has_stripe": bool(account.stripe_customer_id),
    }


@router.post("/checkout")
@limiter.limit("10/hour")
async def create_checkout(
    request: Request,
    body: CheckoutRequest,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Checkout session for upgrading to Pro."""
    _init_stripe()

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
            update(Account)
            .where(Account.id == account.id)
            .values(stripe_customer_id=customer_id)
        )
        await db.commit()

    # Look up the Pro price from Stripe
    # Convention: product with metadata lightpaper_tier=pro
    prices = stripe.Price.list(active=True, limit=10)
    pro_price = None
    for price in prices.data:
        product = stripe.Product.retrieve(price.product)
        if product.metadata.get("lightpaper_tier") == "pro":
            pro_price = price
            break

    if not pro_price:
        raise HTTPException(
            status_code=503,
            detail="Pro plan not configured in Stripe. Create a product with metadata lightpaper_tier=pro.",
        )

    base_url = settings.base_url
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": pro_price.id, "quantity": 1}],
        success_url=f"{base_url}{body.success_url}",
        cancel_url=f"{base_url}{body.cancel_url}",
        metadata={"lightpaper_account_id": str(account.id)},
    )

    return {"checkout_url": checkout_session.url}


@router.post("/portal")
@limiter.limit("10/hour")
async def create_portal(
    request: Request,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Billing Portal session for managing subscription."""
    _init_stripe()

    if not account.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account. Subscribe to Pro first.")

    portal_session = stripe.billing_portal.Session.create(
        customer=account.stripe_customer_id,
        return_url=f"{settings.base_url}/write",
    )
    return {"portal_url": portal_session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data, db)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_cancelled(data, db)
    elif event_type == "invoice.payment_failed":
        logger.warning("Payment failed for customer %s", data.get("customer"))

    return Response(status_code=200)


# --- Webhook handlers ---


async def _handle_checkout_completed(session_data: dict, db: AsyncSession):
    """Upgrade account to pro after successful checkout."""
    customer_id = session_data.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(Account).where(Account.stripe_customer_id == customer_id)
    )
    account = result.scalar_one_or_none()
    if not account:
        # Try metadata fallback
        account_id = session_data.get("metadata", {}).get("lightpaper_account_id")
        if account_id:
            result = await db.execute(
                select(Account).where(Account.id == account_id)
            )
            account = result.scalar_one_or_none()

    if account:
        await db.execute(
            update(Account)
            .where(Account.id == account.id)
            .values(tier="pro", stripe_customer_id=customer_id)
        )
        await db.commit()
        logger.info("Account %s upgraded to pro", account.id)


async def _handle_subscription_cancelled(subscription_data: dict, db: AsyncSession):
    """Downgrade account to free when subscription is cancelled."""
    customer_id = subscription_data.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(Account).where(Account.stripe_customer_id == customer_id)
    )
    account = result.scalar_one_or_none()
    if account:
        await db.execute(
            update(Account)
            .where(Account.id == account.id)
            .values(tier="free")
        )
        await db.commit()
        logger.info("Account %s downgraded to free", account.id)
