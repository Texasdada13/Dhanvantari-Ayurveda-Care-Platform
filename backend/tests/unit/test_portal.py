"""Patient portal: token-only (unauthenticated) access. CRITICAL security surface."""
import pytest
import pytest_asyncio
import secrets

from app.models.patient import Patient
from app.models.checkin import CheckInToken


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def patient_with_token(db_session, practitioner):
    """Create a patient + their portal token, return (patient, token_string)."""
    p = Patient(practitioner_id=practitioner.id, first_name="Pat", last_name="Ient")
    db_session.add(p)
    await db_session.flush()
    tok = CheckInToken(patient_id=p.id, token=secrets.token_urlsafe(32))
    db_session.add(tok)
    await db_session.commit()
    await db_session.refresh(p)
    await db_session.refresh(tok)
    return p, tok.token


# ── Valid access ──────────────────────────────────────────────────────────────

async def test_portal_home_valid_token(client, patient_with_token):
    _, token = patient_with_token
    r = await client.get(f"/api/portal/{token}")
    assert r.status_code == 200
    data = r.json()
    assert data["patient"]["first_name"] == "Pat"
    assert data["today_checkin_done"] is False
    assert data["streak"] == 0


# ── Invalid tokens (security) ─────────────────────────────────────────────────

async def test_portal_unknown_token_404(client):
    r = await client.get("/api/portal/not-a-real-token")
    assert r.status_code == 404


async def test_portal_sql_injection_attempt(client):
    """Token with SQL-injection chars must 404, not crash or leak."""
    r = await client.get("/api/portal/' OR 1=1--")
    assert r.status_code in (404, 422)


async def test_portal_empty_token_not_auth(client):
    r = await client.get("/api/portal/")
    assert r.status_code in (404, 405)  # depends on routing


async def test_portal_deactivated_token_rejected(client, db_session, patient_with_token):
    _, token = patient_with_token
    # Deactivate the token
    from sqlalchemy import select
    t = (await db_session.execute(select(CheckInToken).where(CheckInToken.token == token))).scalar_one()
    t.active = False
    await db_session.commit()

    r = await client.get(f"/api/portal/{token}")
    assert r.status_code == 404


async def test_portal_inactive_patient_rejected(client, db_session, patient_with_token):
    patient, token = patient_with_token
    patient.active = False
    await db_session.commit()

    r = await client.get(f"/api/portal/{token}")
    assert r.status_code == 404


# ── Cross-patient data isolation via token ────────────────────────────────────

async def test_portal_token_is_patient_scoped(client, db_session, practitioner):
    """Each patient's token returns only that patient's data — never cross-leak."""
    from app.models.patient import Patient
    from app.models.checkin import CheckInToken
    p1 = Patient(practitioner_id=practitioner.id, first_name="Alice", last_name="A")
    p2 = Patient(practitioner_id=practitioner.id, first_name="Bob",   last_name="B")
    db_session.add_all([p1, p2])
    await db_session.flush()
    t1 = CheckInToken(patient_id=p1.id, token="tok-alice-xxxxxxxx")
    t2 = CheckInToken(patient_id=p2.id, token="tok-bob-xxxxxxxx")
    db_session.add_all([t1, t2])
    await db_session.commit()

    r1 = await client.get(f"/api/portal/{t1.token}")
    r2 = await client.get(f"/api/portal/{t2.token}")
    assert r1.json()["patient"]["first_name"] == "Alice"
    assert r2.json()["patient"]["first_name"] == "Bob"


# ── Check-in submission ───────────────────────────────────────────────────────

async def test_portal_checkin_submit(client, patient_with_token):
    _, token = patient_with_token
    r = await client.post(f"/api/portal/{token}/checkin", json={
        "warm_water": True, "breathing_exercise": True, "digestion_score": 4,
    })
    assert r.status_code == 201
    data = r.json()
    assert "habit_completion_pct" in data


async def test_portal_duplicate_checkin_same_day_rejected(client, patient_with_token):
    _, token = patient_with_token
    r1 = await client.post(f"/api/portal/{token}/checkin", json={"warm_water": True})
    assert r1.status_code == 201
    r2 = await client.post(f"/api/portal/{token}/checkin", json={"warm_water": False})
    assert r2.status_code == 409


async def test_portal_checkin_with_bad_token_404(client):
    r = await client.post("/api/portal/bad-token/checkin", json={"warm_water": True})
    assert r.status_code == 404


async def test_portal_checkin_scores_validated(client, patient_with_token):
    """Score fields should accept int or null — extreme values should not crash."""
    _, token = patient_with_token
    r = await client.post(f"/api/portal/{token}/checkin", json={
        "digestion_score": 99999,  # unvalidated — app should accept or reject cleanly
    })
    # Either accept or 422 — must not 500
    assert r.status_code in (201, 422)


# ── Portal endpoints NO AUTH required (by design) ─────────────────────────────

async def test_portal_plan_no_auth_header_needed(client, patient_with_token):
    """Portal is designed for unauthenticated access via token only."""
    _, token = patient_with_token
    r = await client.get(f"/api/portal/{token}/plan")
    # 404 because no plan exists yet — but the call itself was allowed
    assert r.status_code == 404


async def test_portal_history_empty_ok(client, patient_with_token):
    _, token = patient_with_token
    r = await client.get(f"/api/portal/{token}/history")
    assert r.status_code == 200
    assert r.json()["checkins"] == []
