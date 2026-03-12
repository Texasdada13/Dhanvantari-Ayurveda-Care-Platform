"""
Billing routes — Stripe checkout sessions, webhooks, billing portal.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_practitioner
from app.models.practitioner import Practitioner, SubscriptionTier
from app.models.billing import Subscription

router = APIRouter()

TIER_PRICE_MAP = {
    "seed": settings.STRIPE_PRICE_SEED,
    "practice": settings.STRIPE_PRICE_PRACTICE,
    "clinic": settings.STRIPE_PRICE_CLINIC,
}

PRICE_TIER_MAP = {v: k for k, v in TIER_PRICE_MAP.items() if v}


class CheckoutRequest(BaseModel):
    tier: str


# ── Stripe helper ─────────────────────────────────────────────────────────────

def _get_stripe():
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/checkout")
async def create_checkout_session(
    body: CheckoutRequest,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    if body.tier not in TIER_PRICE_MAP:
        raise HTTPException(status_code=400, detail="Invalid tier. Choose: seed, practice, clinic")

    price_id = TIER_PRICE_MAP[body.tier]
    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe price not configured for this tier")

    stripe = _get_stripe()

    # Get or create Stripe customer
    customer_id = practitioner.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=practitioner.email,
            name=practitioner.name,
            metadata={"practitioner_id": str(practitioner.id)},
        )
        customer_id = customer.id
        practitioner.stripe_customer_id = customer_id
        await db.flush()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.FRONTEND_URL}/dashboard?billing=success",
        cancel_url=f"{settings.FRONTEND_URL}/pricing?billing=cancelled",
        metadata={"practitioner_id": str(practitioner.id), "tier": body.tier},
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    stripe = _get_stripe()
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        practitioner_id = int(session["metadata"].get("practitioner_id", 0))
        tier = session["metadata"].get("tier", "seed")
        await _activate_subscription(db, practitioner_id, tier, session.get("subscription"))

    elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        await _sync_subscription(db, sub)

    return {"received": True}


async def _activate_subscription(db: AsyncSession, practitioner_id: int, tier: str, stripe_sub_id: str | None):
    result = await db.execute(select(Practitioner).where(Practitioner.id == practitioner_id))
    p = result.scalars().first()
    if not p:
        return

    p.subscription_tier = tier
    p.subscription_active = True

    if stripe_sub_id:
        result = await db.execute(
            select(Subscription).where(Subscription.practitioner_id == practitioner_id)
        )
        sub = result.scalars().first()
        if not sub:
            sub = Subscription(practitioner_id=practitioner_id, stripe_subscription_id=stripe_sub_id, tier=tier, status="active")
            db.add(sub)
        else:
            sub.stripe_subscription_id = stripe_sub_id
            sub.tier = tier
            sub.status = "active"


async def _sync_subscription(db: AsyncSession, stripe_sub: dict):
    sub_id = stripe_sub["id"]
    result = await db.execute(select(Subscription).where(Subscription.stripe_subscription_id == sub_id))
    sub = result.scalars().first()
    if not sub:
        return

    sub.status = stripe_sub["status"]
    sub.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)

    if stripe_sub.get("current_period_end"):
        sub.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"], tz=timezone.utc)

    # Update practitioner tier
    result = await db.execute(select(Practitioner).where(Practitioner.id == sub.practitioner_id))
    p = result.scalars().first()
    if p:
        p.subscription_active = stripe_sub["status"] in ("active", "trialing")


@router.post("/portal")
async def create_billing_portal_session(
    practitioner: Practitioner = Depends(get_current_practitioner),
):
    if not practitioner.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found. Please subscribe first.")

    stripe = _get_stripe()
    session = stripe.billing_portal.Session.create(
        customer=practitioner.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/dashboard/settings",
    )
    return {"portal_url": session.url}


@router.get("/subscription")
async def get_subscription(
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime
    now = datetime.now(timezone.utc)
    in_trial = bool(practitioner.trial_ends_at and practitioner.trial_ends_at > now and not practitioner.subscription_active)

    result = await db.execute(
        select(Subscription).where(Subscription.practitioner_id == practitioner.id)
    )
    sub = result.scalars().first()

    return {
        "tier": practitioner.subscription_tier,
        "active": practitioner.subscription_active,
        "in_trial": in_trial,
        "trial_ends_at": practitioner.trial_ends_at.isoformat() if practitioner.trial_ends_at else None,
        "subscription": {
            "status": sub.status,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "cancel_at_period_end": sub.cancel_at_period_end,
        } if sub else None,
    }
