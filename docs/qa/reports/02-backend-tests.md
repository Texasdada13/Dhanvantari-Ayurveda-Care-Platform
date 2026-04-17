# Phase 2 — Backend Test Report

**Run date:** 2026-04-16
**Engine:** pytest 8.3 + pytest-asyncio 0.24 against real Postgres 16 (docker-compose)
**Duration:** ~56s for 52 tests

## Summary

| Result | Count |
|--------|-------|
| Passed | 47 |
| XFail (known bug) | 5 |
| Failed | 0 |
| Total | 52 |

## Test Suites

### `test_auth.py` — 20 tests, all passed
- Registration: creates practitioner, rejects duplicates, lowercases email, validates format
- Login: success, wrong password, unknown email, case-insensitive, deactivated account
- /me: valid token, no token, bad token, refresh-token-as-access, expired token
- Refresh: issues new tokens, rejects access token, rejects garbage
- Token mechanics: roundtrip, bad token, tampered signature

### `test_patients.py` — 11 tests (6 passed, 5 xfailed)
- List patients (empty): PASS
- Unknown patient 404: PASS
- Multi-tenant isolation: PASS — **cross-practitioner access correctly blocked**
- Auth required: PASS
- Subscription required (expired trial → 402): PASS
- Seed tier 30-patient limit: PASS
- CRUD operations: 5 XFAIL (see Known Bugs below)

### `test_portal.py` — 13 tests, all passed
- Valid token access: PASS
- Invalid/unknown/empty tokens: PASS (404)
- SQL injection token: PASS (404, no crash)
- Deactivated token rejected: PASS
- Inactive patient rejected: PASS
- Patient data isolation across tokens: PASS
- Check-in: submit, duplicate-day prevention, bad token
- Score field boundary (extreme value): PASS (accepted)
- No auth header required (by design): PASS
- Empty history: PASS

### `test_billing.py` — 8 tests, all passed
- Webhook: missing signature blocked, bad signature blocked
- Subscription: returns tier data, requires auth
- Checkout: rejects invalid tier, rejects unconfigured price, requires auth
- Billing portal: rejects when no Stripe customer

## Known Bugs (Production Blockers)

### BUG-001: MissingGreenlet in patient CRUD routes (CRITICAL)

**Severity:** Critical — affects all patient create/read/update/delete operations
**Affected code:** `backend/app/api/routes/patients.py` — `_patient_summary()` at line 210-211
**Root cause:** The function accesses `p.health_profile.dosha_primary` and `p.checkin_token.token` as lazy-load attributes on SQLAlchemy async session. Async sessions forbid implicit lazy-loading — it triggers `MissingGreenlet` error.

This fails on **both SQLite AND real Postgres** — it is NOT a test-only issue.

**Impact:** Any API call that creates, reads, updates, or deletes a patient will 500 in production IF:
- The patient doesn't have a pre-loaded (eagerly fetched) health_profile/checkin_token
- The route uses `_patient_summary()` to serialize the response

**Reproduction:**
```bash
cd backend && python -m pytest tests/unit/test_patients.py::test_create_patient -x --tb=short
```

**Recommended fix (choose one):**
1. **(Preferred)** In `create_patient`, after `db.flush()`, set `hp.patient = patient` and `tok.patient = patient` so back_populates wires the relationship in-memory (no SQL needed).
2. In `_patient_summary`, guard with `try/except` and use `getattr(p, 'health_profile', None)` if loaded.
3. Add `await db.refresh(patient, ['health_profile', 'checkin_token'])` after flush.

## Security Findings

- Portal SQL injection attempt: returns 404 cleanly (no leak)
- Multi-tenant isolation: correctly enforced
- Token deactivation: correctly enforced
- Stripe webhook signature: correctly verified
- Subscription tier limits: correctly enforced

## Coverage Gap Assessment

| Area | Coverage | Notes |
|------|----------|-------|
| Auth (register/login/me/refresh) | **Strong** | 20 tests including negative cases |
| Patients (CRUD) | Blocked | xfail due to BUG-001 |
| Patients (authz/isolation) | **Strong** | Multi-tenant, tier-limit, sub-required |
| Portal | **Strong** | 13 tests, good security coverage |
| Billing | **Good** | Webhook, checkout, subscription |
| AI endpoints | Gap | Not tested (requires API key mock) |
| Plans | Gap | Blocked by BUG-001 (same _patient_summary dependency) |
| Yoga/Pranayama/Supplements | Gap | CRUD with auth — would pass same pattern as auth tests |
| Assessments | Gap | Not tested |
| Consultation notes | Gap | Not tested |

## Artifacts
- `backend/pytest.ini`
- `backend/tests/conftest.py`
- `backend/tests/unit/test_auth.py` (20 tests)
- `backend/tests/unit/test_patients.py` (11 tests, 5 xfail)
- `backend/tests/unit/test_portal.py` (13 tests)
- `backend/tests/unit/test_billing.py` (8 tests)
