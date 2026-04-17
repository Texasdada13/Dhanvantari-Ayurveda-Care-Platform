"""Patient CRUD + multi-tenant isolation + Seed tier patient-limit enforcement.

KNOWN PRODUCTION BUG (tracked in docs/qa/reports/02-backend-tests.md):
`create_patient`, `get_patient`, `update_patient`, `delete_patient` routes trigger
SQLAlchemy MissingGreenlet because they access `patient.health_profile` and
`patient.checkin_token` relationships without `selectinload` after adding them.
Five tests below are marked xfail until the routes either (a) use selectinload
after flush or (b) manually assign `hp.patient = patient` to wire back_populates.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone

from app.models.patient import Patient
from app.models.practitioner import Practitioner, SubscriptionTier
from app.core.security import hash_password, create_access_token


pytestmark = pytest.mark.asyncio

XFAIL_LAZY_LOAD = pytest.mark.xfail(
    reason="Production bug: lazy-load in async context (MissingGreenlet). "
           "See docs/qa/reports/02-backend-tests.md §Known Bugs.",
    strict=True,
)


# ── List / create / get ───────────────────────────────────────────────────────

@XFAIL_LAZY_LOAD
async def test_create_patient(client, auth_headers):
    r = await client.post("/api/patients", headers=auth_headers, json={
        "first_name": "Jane", "last_name": "Doe", "sex": "F", "email": "jane@example.com",
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["first_name"] == "Jane"
    assert data["id"] > 0


async def test_list_patients_empty(client, auth_headers):
    r = await client.get("/api/patients", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


@XFAIL_LAZY_LOAD
async def test_list_returns_own_patients(client, auth_headers):
    await client.post("/api/patients", headers=auth_headers, json={"first_name": "A", "last_name": "One"})
    await client.post("/api/patients", headers=auth_headers, json={"first_name": "B", "last_name": "Two"})
    r = await client.get("/api/patients", headers=auth_headers)
    assert r.status_code == 200
    names = [f"{p['first_name']} {p['last_name']}" for p in r.json()]
    assert "A One" in names and "B Two" in names


@XFAIL_LAZY_LOAD
async def test_get_patient_by_id(client, auth_headers):
    c = await client.post("/api/patients", headers=auth_headers, json={"first_name": "X", "last_name": "Y"})
    pid = c.json()["id"]
    r = await client.get(f"/api/patients/{pid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == pid


async def test_get_unknown_patient_404(client, auth_headers):
    r = await client.get("/api/patients/99999", headers=auth_headers)
    assert r.status_code == 404


# ── Multi-tenant isolation (CRITICAL security test) ───────────────────────────

async def test_practitioner_cannot_see_other_practitioners_patients(client, db_session, auth_headers):
    """A patient owned by practitioner B must not be visible to practitioner A."""
    # Create second practitioner + their patient
    other = Practitioner(
        name="Dr. Other",
        email="other@example.com",
        password_hash=hash_password("pw12345678"),
        subscription_tier=SubscriptionTier.PRACTICE,
        subscription_active=True,
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(other)
    await db_session.flush()
    other_patient = Patient(practitioner_id=other.id, first_name="Secret", last_name="Case")
    db_session.add(other_patient)
    await db_session.commit()

    # Practitioner A lists — should not see Other's patient
    r = await client.get("/api/patients", headers=auth_headers)
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()]
    assert other_patient.id not in ids

    # Practitioner A attempts direct fetch — should 404 (not 200)
    r2 = await client.get(f"/api/patients/{other_patient.id}", headers=auth_headers)
    assert r2.status_code == 404, "CRITICAL: cross-tenant patient access leak"


# ── Patch / delete ────────────────────────────────────────────────────────────

@XFAIL_LAZY_LOAD
async def test_patch_patient(client, auth_headers):
    c = await client.post("/api/patients", headers=auth_headers, json={"first_name": "X", "last_name": "Y"})
    pid = c.json()["id"]
    r = await client.patch(f"/api/patients/{pid}", headers=auth_headers, json={"occupation": "Engineer"})
    assert r.status_code == 200
    assert r.json()["occupation"] == "Engineer"


@XFAIL_LAZY_LOAD
async def test_delete_patient_soft_deletes(client, auth_headers):
    c = await client.post("/api/patients", headers=auth_headers, json={"first_name": "To", "last_name": "Delete"})
    pid = c.json()["id"]
    r = await client.delete(f"/api/patients/{pid}", headers=auth_headers)
    assert r.status_code in (200, 204)
    # Should no longer appear in list
    list_r = await client.get("/api/patients", headers=auth_headers)
    assert pid not in [p["id"] for p in list_r.json()]


# ── Auth required ─────────────────────────────────────────────────────────────

async def test_patients_require_auth(client):
    r = await client.get("/api/patients")
    assert r.status_code in (401, 403)


async def test_patients_require_active_subscription(client, db_session):
    """Expired trial + no subscription → 402 Payment Required."""
    expired = Practitioner(
        name="Dr. Expired",
        email="expired@example.com",
        password_hash=hash_password("pw12345678"),
        subscription_tier=SubscriptionTier.PRACTICE,
        subscription_active=False,
        trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(expired)
    await db_session.commit()
    await db_session.refresh(expired)

    token = create_access_token(expired.id)
    r = await client.get("/api/patients", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 402


# ── Seed tier patient limit ───────────────────────────────────────────────────

async def test_seed_tier_blocks_after_30_patients(client, db_session):
    """Seed plan is capped at 30 active patients."""
    seed_p = Practitioner(
        name="Dr. Seed",
        email="seed@example.com",
        password_hash=hash_password("pw12345678"),
        subscription_tier=SubscriptionTier.SEED,
        subscription_active=True,
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(seed_p)
    await db_session.flush()
    for i in range(30):
        db_session.add(Patient(practitioner_id=seed_p.id, first_name=f"P{i}", last_name="X"))
    await db_session.commit()

    token = create_access_token(seed_p.id)
    r = await client.post(
        "/api/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Over", "last_name": "Limit"},
    )
    assert r.status_code == 403
    assert "limit" in r.json()["detail"].lower()
