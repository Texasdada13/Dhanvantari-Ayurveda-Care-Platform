"""
Shared pytest fixtures for backend tests.

Connects to real Postgres (via docker-compose on localhost:5432 by default).
Each test gets a fresh schema (drop + create all tables) for full isolation.

Override TEST_DATABASE_URL env var to point at a different instance in CI.
"""
import asyncio
import os

# ── Environment: must be set BEFORE importing the app ─────────────────────────
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/dhanvantari",
)
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production-use")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("STRIPE_SECRET_KEY", "")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "")
os.environ.setdefault("RESEND_API_KEY", "")

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Import AFTER env is set
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.main import app
from app.models.practitioner import Practitioner, SubscriptionTier


# ── Event loop ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Engine / schema lifecycle ────────────────────────────────────────────────
# One engine per session (expensive to create). Schema is dropped+recreated per
# test so tests see a clean DB.

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False, future=True)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def _reset_schema(engine):
    """Drop + recreate all tables before every test. Ensures full isolation."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncSession:
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(engine) -> AsyncClient:
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_get_db():
        async with session_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Domain fixtures ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def practitioner(db_session) -> Practitioner:
    p = Practitioner(
        name="Dr. Test",
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        practice_name="Test Clinic",
        subscription_tier=SubscriptionTier.PRACTICE,
        subscription_active=True,
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)
    return p


@pytest.fixture
def auth_headers(practitioner) -> dict:
    token = create_access_token(practitioner.id)
    return {"Authorization": f"Bearer {token}"}
