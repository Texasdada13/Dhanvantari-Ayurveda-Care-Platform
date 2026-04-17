"""Auth endpoint tests: register, login, refresh, /me, token validation."""
import pytest
from app.core.security import create_access_token, create_refresh_token, decode_token


pytestmark = pytest.mark.asyncio


# ── Registration ──────────────────────────────────────────────────────────────

async def test_register_creates_practitioner(client):
    r = await client.post("/api/auth/register", json={
        "name": "Dr. Smith",
        "email": "smith@example.com",
        "password": "strongpass123",
        "practice_name": "Smith Clinic",
        "designation": "BAMS",
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert "access_token" in data and "refresh_token" in data
    assert data["practitioner"]["email"] == "smith@example.com"
    assert data["practitioner"]["in_trial"] is True


async def test_register_rejects_duplicate_email(client):
    payload = {"name": "A", "email": "dup@example.com", "password": "x12345678"}
    r1 = await client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already registered" in r2.json()["detail"].lower()


async def test_register_lowercases_email(client):
    r = await client.post("/api/auth/register", json={
        "name": "A", "email": "MiXeD@Example.COM", "password": "x12345678",
    })
    assert r.status_code == 201
    assert r.json()["practitioner"]["email"] == "mixed@example.com"


async def test_register_rejects_invalid_email(client):
    r = await client.post("/api/auth/register", json={
        "name": "A", "email": "not-an-email", "password": "x12345678",
    })
    assert r.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_success(client, practitioner):
    r = await client.post("/api/auth/login", json={
        "email": practitioner.email, "password": "testpass123",
    })
    assert r.status_code == 200
    assert r.json()["practitioner"]["id"] == practitioner.id


async def test_login_wrong_password(client, practitioner):
    r = await client.post("/api/auth/login", json={
        "email": practitioner.email, "password": "wrong-password",
    })
    assert r.status_code == 401


async def test_login_unknown_email(client):
    r = await client.post("/api/auth/login", json={
        "email": "nobody@example.com", "password": "anything",
    })
    assert r.status_code == 401


async def test_login_email_case_insensitive(client, practitioner):
    r = await client.post("/api/auth/login", json={
        "email": practitioner.email.upper(), "password": "testpass123",
    })
    assert r.status_code == 200


async def test_login_deactivated_account(client, db_session, practitioner):
    practitioner.active = False
    await db_session.commit()
    r = await client.post("/api/auth/login", json={
        "email": practitioner.email, "password": "testpass123",
    })
    assert r.status_code == 403


# ── /me ───────────────────────────────────────────────────────────────────────

async def test_me_returns_practitioner(client, auth_headers, practitioner):
    r = await client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == practitioner.id


async def test_me_rejects_no_token(client):
    r = await client.get("/api/auth/me")
    assert r.status_code == 403  # HTTPBearer returns 403 when header absent


async def test_me_rejects_bad_token(client):
    r = await client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert r.status_code == 401


async def test_me_rejects_refresh_token_as_access(client, practitioner):
    refresh = create_refresh_token(practitioner.id)
    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {refresh}"})
    # Refresh token has type=refresh, should be rejected by deps.get_current_practitioner
    assert r.status_code == 401


async def test_me_rejects_expired_token(client, practitioner):
    from datetime import timedelta
    expired = create_access_token(practitioner.id, expires_delta=timedelta(seconds=-1))
    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


# ── Refresh ───────────────────────────────────────────────────────────────────

async def test_refresh_issues_new_tokens(client, practitioner):
    refresh = create_refresh_token(practitioner.id)
    r = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data and "refresh_token" in data


async def test_refresh_rejects_access_token(client, practitioner):
    access = create_access_token(practitioner.id)
    r = await client.post("/api/auth/refresh", json={"refresh_token": access})
    # Access token has type=access, should be rejected
    assert r.status_code == 401


async def test_refresh_rejects_garbage(client):
    r = await client.post("/api/auth/refresh", json={"refresh_token": "garbage"})
    assert r.status_code == 401


# ── Token mechanics ───────────────────────────────────────────────────────────

def test_token_roundtrip():
    t = create_access_token(42)
    payload = decode_token(t)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_decode_bad_token_returns_empty():
    assert decode_token("not.a.jwt") == {}


def test_decode_tampered_signature_returns_empty():
    t = create_access_token(1)
    tampered = t[:-5] + "XXXXX"
    assert decode_token(tampered) == {}
