"""Billing endpoints — Stripe webhook signature & subscription lifecycle."""
import pytest

pytestmark = pytest.mark.asyncio


# ── Webhook signature enforcement (CRITICAL) ──────────────────────────────────

async def test_webhook_rejects_missing_signature(client):
    """A webhook call with no signature header must NOT be processed."""
    r = await client.post("/api/billing/webhook", json={"type": "checkout.session.completed"})
    # Either 400 (no signature) or 500 (webhook secret not configured).
    # Must NOT be 200 — a 200 would mean webhook processed without validation.
    assert r.status_code in (400, 422, 500)


async def test_webhook_rejects_bad_signature(client, monkeypatch):
    """A webhook with bogus signature must 400, not activate a subscription."""
    from app.core import config
    monkeypatch.setattr(config.settings, "STRIPE_WEBHOOK_SECRET", "whsec_test")

    r = await client.post(
        "/api/billing/webhook",
        headers={"stripe-signature": "bogus"},
        json={"type": "checkout.session.completed"},
    )
    assert r.status_code == 400


# ── Subscription status ───────────────────────────────────────────────────────

async def test_get_subscription_for_trial_practitioner(client, auth_headers, practitioner):
    r = await client.get("/api/billing/subscription", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "tier" in data
    assert data["active"] is True  # our fixture sets active=True


async def test_get_subscription_requires_auth(client):
    r = await client.get("/api/billing/subscription")
    assert r.status_code in (401, 403)


# ── Checkout validation ───────────────────────────────────────────────────────

async def test_checkout_rejects_invalid_tier(client, auth_headers):
    r = await client.post("/api/billing/checkout", headers=auth_headers, json={"tier": "unicorn"})
    assert r.status_code == 400
    assert "invalid tier" in r.json()["detail"].lower()


async def test_checkout_rejects_when_price_not_configured(client, auth_headers):
    """With empty STRIPE_PRICE_* env vars (our default), valid tier should 500 cleanly."""
    r = await client.post("/api/billing/checkout", headers=auth_headers, json={"tier": "seed"})
    # Either 500 (price not configured) or 400 — must not 200
    assert r.status_code in (400, 500)


async def test_checkout_requires_auth(client):
    r = await client.post("/api/billing/checkout", json={"tier": "seed"})
    assert r.status_code in (401, 403)


# ── Portal ────────────────────────────────────────────────────────────────────

async def test_billing_portal_rejects_when_no_customer(client, auth_headers):
    """Practitioner without stripe_customer_id can't open billing portal."""
    r = await client.post("/api/billing/portal", headers=auth_headers)
    assert r.status_code == 400
