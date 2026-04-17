# Phase 3 — Integration Test Report

**Run date:** 2026-04-16
**DB:** PostgreSQL 16 (docker-compose `postgres:16-alpine`)

## Summary

Integration testing was **merged with Phase 2** — all 52 backend tests ran against real Postgres 16 via docker-compose, NOT SQLite mocks. This gives us true integration coverage:

- Tables created via `Base.metadata.create_all` (full ORM → DDL)
- All queries executed against real Postgres (asyncpg driver)
- FK constraints, unique constraints, enum types all verified
- Timezone-aware datetimes verified (PostgreSQL `timestamptz`)

## What Was Verified

| Integration Point | Status | Notes |
|-------------------|--------|-------|
| asyncpg connectivity | PASS | Tests connect and execute |
| Table creation (DDL) | PASS | All models create tables cleanly |
| FK constraints | PASS | Patient → Practitioner, CheckInToken → Patient |
| Unique constraints | PASS | Email uniqueness on practitioners |
| Enum columns | PASS | SubscriptionTier serializes correctly |
| DateTime(timezone=True) | PASS | UTC timestamps round-trip correctly |
| Boolean comparisons | PASS | `== True` filters work on Postgres |
| Auth token flow | PASS | End-to-end JWT → DB → response |
| Portal token resolution | PASS | Token lookup + patient join works |

## Not Tested (requires running application)

- **Alembic migrations** — Schema was created via `create_all`, not via Alembic. Migration testing is in Phase 6 (deployment readiness).
- **Connection pooling** — Tests use per-test sessions, not the app's pool.
- **Transaction isolation** — Each test gets a clean schema drop+recreate.

## Verdict

Integration layer is healthy. The Postgres-backed test run validates that the ORM models, queries, and constraints work correctly against the production database engine.
