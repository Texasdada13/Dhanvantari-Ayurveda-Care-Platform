# Production QA Implementation Plan

**Spec:** `docs/superpowers/specs/2026-04-16-production-qa-design.md`
**Execution mode:** Autonomous (user AFK)
**Stop conditions:** (a) destructive operation needed, (b) requires prod secrets, (c) requires push/deploy

## Execution Order (phases run sequentially except where parallel)

### Phase 1 — Static Analysis  *(parallel subtasks)*
- **1.1** Frontend: `npm run lint` — capture ESLint output
- **1.2** Frontend: `npx tsc --noEmit` — TypeScript check
- **1.3** Frontend: `npm audit --json` — dependency CVEs
- **1.4** Backend: install + run `ruff check app/` — Python lint
- **1.5** Backend: `pip-audit` — Python dependency CVEs
- **1.6** Secret scan: grep for common leak patterns (`sk-ant`, `sk_live_`, AWS keys, hardcoded secrets)
- **1.7** Dockerfile lint (frontend + backend)
- **Artifact:** `docs/qa/reports/01-static-analysis.md`

### Phase 2 — Backend Unit Tests
- **2.1** Create `backend/pytest.ini` with asyncio mode + test paths
- **2.2** Create `backend/tests/conftest.py` — async client, test DB (sqlite aiosqlite), auth token fixture
- **2.3** Write `tests/unit/test_auth.py` — register, login, wrong pw, expired token, `/me`
- **2.4** Write `tests/unit/test_patients.py` — CRUD, practitioner isolation
- **2.5** Write `tests/unit/test_plans.py` — create, patch, supplements + recipes attach
- **2.6** Write `tests/unit/test_portal.py` — valid token, invalid token, check-in submit
- **2.7** Write `tests/unit/test_assessments.py` — dosha score math
- **2.8** Write `tests/unit/test_billing.py` — Stripe webhook signature, checkout session mock
- **2.9** Run suite, capture results → `docs/qa/reports/02-backend-tests.md`

### Phase 3 — Integration Tests (real Postgres)
- **3.1** Bring up `docker compose up -d postgres` (if docker available)
- **3.2** Run `alembic upgrade head` against it
- **3.3** Run `tests/integration/` with `TEST_DATABASE_URL` env set
- **3.4** Tear down
- **Artifact:** `docs/qa/reports/03-integration-tests.md`
- **Fallback if Docker unavailable:** document and skip; note in deployment-readiness

### Phase 4 — Frontend Tests (Vitest)
- **4.1** `npm i -D vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom jsdom msw`
- **4.2** Create `vitest.config.ts` + `vitest.setup.ts`
- **4.3** Add `test` + `test:coverage` scripts to `package.json`
- **4.4** Write `src/lib/api.test.ts` — axios interceptor, auth header
- **4.5** Write `src/components/dosha-radar-chart.test.tsx`
- **4.6** Write `src/components/ai/*.test.tsx` — loading/error states
- **4.7** Run suite → `docs/qa/reports/04-frontend-tests.md`

### Phase 5 — E2E (Playwright)
- **5.1** `npm i -D @playwright/test` + `npx playwright install chromium`
- **5.2** `playwright.config.ts` — baseURL from env, webServer hook optional
- **5.3** `e2e/auth.spec.ts` — login with demo creds, logout, bad creds
- **5.4** `e2e/patient-flow.spec.ts` — create patient, assign plan, print
- **5.5** `e2e/portal.spec.ts` — open portal via token, submit check-in
- **5.6** Run against docker-compose stack if available
- **Artifact:** `docs/qa/reports/05-e2e-tests.md` (tests may be written but skipped to run — noted explicitly)

### Phase 6 — Deployment Readiness
- **6.1** `docker build` backend → capture image size, warnings
- **6.2** `docker build` frontend → capture image size, warnings
- **6.3** Validate `render.yaml` shape (required fields, env var references)
- **6.4** Migration dry-run: start postgres, run `alembic upgrade head`, confirm no errors, `alembic downgrade base` then `upgrade head` to test idempotency
- **6.5** Check `/api/health` endpoint works via running backend
- **6.6** Verify CORS rejects unlisted origins
- **6.7** Audit startup demo-user creation — document production risk
- **Artifact:** `docs/qa/reports/06-deployment-readiness.md`

### Phase 7 — Performance + Accessibility
- **7.1** `perf/k6-smoke.js` — 30s ramp, /api/health and /api/auth/login, capture p50/p95
- **7.2** Frontend bundle analysis — `next build` output + budget comparison
- **7.3** Lighthouse CI: `npx @lhci/cli autorun` on built frontend (if stack running) — else document
- **7.4** `axe-core` via Playwright — run on dashboard + portal pages
- **Artifact:** `docs/qa/reports/07-performance.md` + `09-accessibility.md`

### Phase 8 — Security Deep Dive
- **8.1** `pip install bandit && bandit -r backend/app` — Python SAST
- **8.2** OWASP Top 10 manual code review checklist (A01–A10)
  - A01 Broken Access Control — review every route's auth decorator
  - A02 Crypto Failures — verify bcrypt + JWT algorithm + no cleartext PHI
  - A03 Injection — SQLAlchemy parameterized; manual check any raw SQL
  - A04 Insecure Design — portal token entropy, session lifetime
  - A05 Misconfig — DEBUG flag, CORS, TrustedHost
  - A06 Vulnerable Components — cross-ref with Phase 1 audit
  - A07 Auth failures — rate-limit? account lockout?
  - A08 Software/Data Integrity — webhook signature verification
  - A09 Logging — secrets not logged
  - A10 SSRF — any URL fetching in AI handlers?
- **8.3** Negative tests: wrong-practitioner-access, expired token, invalid portal token, SQL-injection strings
- **Artifact:** `docs/qa/reports/08-security.md`

### Phase 9 — UAT Scripts
- **9.1** Practitioner persona journey (registration → patient → plan → print → portal QR)
- **9.2** Patient persona journey (scan QR → view plan → daily check-in)
- **Artifact:** `docs/qa/uat/` folder

### Phase 10 — Executive Summary
- **10.1** Aggregate all report findings into severity buckets
- **10.2** Write go/no-go recommendation
- **10.3** List production blockers and nice-to-haves
- **Artifact:** `docs/qa/reports/00-executive-summary.md`

## Parallelism Strategy

Phases 1 and 2.1–2.2 (setup) can run in parallel via subagents. Phases 4.1–4.2 (frontend setup) can run in parallel with Phase 3.
Phase 10 is strictly sequential (depends on all prior).

## Checkpoints for User Review

Not applicable during AFK — all review happens when user returns. Artifacts are committable but NOT committed/pushed.

## Rollback Plan

All work is new files under `docs/qa/`, `backend/tests/`, `frontend/e2e/`, and configs. Rollback = `git clean -fd docs/qa/ backend/tests/ frontend/e2e/` + revert any config file edits. I will list modified files in the final report so rollback is trivial.

## Stop & Ask Conditions

I will stop and leave a note if I encounter:
- Need to install software outside npm/pip/docker (e.g., k6 binary, Playwright browsers if first install fails)
- Destructive DB operation needed
- Test failures that indicate a real production bug (flag in report, don't silently fix)
- Need for production credentials
- A change to the application source code (source code is yours — tests go in new files only)
