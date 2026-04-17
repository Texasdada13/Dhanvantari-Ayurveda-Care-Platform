# Production QA Design — Dhanvantari Ayurveda Care Platform

**Date:** 2026-04-16
**Author:** Claude Code (autonomous AFK session)
**Status:** Approved autonomously per explicit user instruction ("make the best road map and plan... then execute")
**Deploy target:** Render (3 services: frontend, backend API, managed Postgres)

---

## 1. Problem Statement

The Dhanvantari platform is approaching production deployment on Render. Before go-live, the platform needs rigorous QA coverage that currently does **not exist**:

- `backend/tests/` is empty (pytest is in `requirements.txt` but no tests)
- No frontend test runner configured (no Vitest/Jest)
- No E2E tests
- No performance baselines
- No security scan reports
- No deployment smoke test procedure

This is a **greenfield QA effort** — we must build the test harness *and* generate the first comprehensive QA report in one pass.

## 2. Scope & Success Criteria

### In scope
Industry-standard QA layers for a HIPAA-adjacent health platform:

1. **Static analysis** — lint, type-check, dependency CVEs, secret scan
2. **Unit tests** — backend services + frontend components
3. **Integration tests** — API + real Postgres (from docker-compose)
4. **E2E tests** — Playwright against running frontend+backend
5. **Deployment readiness** — Docker builds, render.yaml validation, migration dry-run, health probes
6. **Performance** — k6 load test, Lighthouse, bundle analysis
7. **Security** — OWASP Top 10 code review, bandit, auth-bypass probes, CORS/CSP
8. **Accessibility** — axe-core / pa11y on key pages
9. **UAT** — scripted persona journeys (practitioner + patient-portal)
10. **Consolidated report** with severity triage and go/no-go recommendation

### Out of scope (flagged for user)
- Tests that require production secrets (live Stripe, live Resend, live Claude API) — mocked only
- Penetration testing beyond OWASP baseline (requires explicit authorization + non-prod environment)
- Mobile responsive visual regression (can be added post-go-live)
- Multi-region/chaos testing (unnecessary for free-tier Render)

### Success criteria
- ✅ Every phase produces an artifact (test file, scan report, or markdown doc)
- ✅ Backend test suite runs to completion (pass/fail captured, not just setup)
- ✅ Final consolidated report has an explicit **GO / NO-GO / GO-WITH-CAVEATS** recommendation
- ✅ All findings categorized by severity (critical / high / medium / low / info)
- ✅ Reproducible: every test documented so the user can re-run locally after AFK session

## 3. Assumptions (documented because user is AFK)

| # | Assumption | Rationale | Reversible? |
|---|------------|-----------|-------------|
| 1 | Use `pytest` + `pytest-asyncio` + `httpx.AsyncClient` for backend tests | Already in `requirements.txt`; canonical FastAPI pattern | Easy to change |
| 2 | Use `Vitest` + `@testing-library/react` for frontend unit/component | Fastest with Vite/Next, React 19 compatible | Could swap for Jest |
| 3 | Use `Playwright` for E2E | Modern, handles Next 16, cross-browser, MS-maintained | Could use Cypress |
| 4 | Use `k6` (CLI) for load tests | Lightweight, scriptable JS, works locally | Could use Locust |
| 5 | Use SQLite-in-memory for *unit* tests, real dockerized Postgres for *integration* | Fast unit loop + realistic integration coverage | Standard split |
| 6 | Mock all third-party APIs (Anthropic, Stripe, Resend) | No prod keys leaked; deterministic tests | Mandatory |
| 7 | Target ≥70% line coverage on backend critical paths (auth, patients, plans, portal, billing) | Realistic for greenfield; full 90% can be a follow-up | Raise later |
| 8 | Treat portal endpoints (no-auth, token-based) as highest security priority | Only unauthenticated API surface | Non-negotiable |
| 9 | Consolidated report in `docs/qa/reports/2026-04-16-production-qa-report.md` | Single source of truth | N/A |
| 10 | Any test/scan failure is documented — NOT silently fixed without user review | Preserves user's code ownership during AFK | Matches "don't overreach" |

**Rule:** I will NOT push to remote, create PRs, merge to master, or deploy during this AFK session. Artifacts are commit-ready but left staged for user review.

## 4. Architecture of the QA System

```
docs/
├── superpowers/
│   ├── specs/2026-04-16-production-qa-design.md   (this file)
│   └── plans/2026-04-16-production-qa-plan.md     (impl plan)
├── qa/
│   ├── reports/
│   │   ├── 00-executive-summary.md                  ← go/no-go
│   │   ├── 01-static-analysis.md
│   │   ├── 02-backend-tests.md
│   │   ├── 03-integration-tests.md
│   │   ├── 04-frontend-tests.md
│   │   ├── 05-e2e-tests.md
│   │   ├── 06-deployment-readiness.md
│   │   ├── 07-performance.md
│   │   ├── 08-security.md
│   │   ├── 09-accessibility.md
│   │   └── 10-uat-scripts.md
│   └── uat/
│       ├── persona-practitioner.md
│       └── persona-patient-portal.md
backend/
├── tests/
│   ├── conftest.py                  (fixtures: db, client, auth token)
│   ├── unit/                        (fast, no DB)
│   ├── integration/                 (real Postgres)
│   └── security/                    (auth-bypass probes)
├── pytest.ini
frontend/
├── vitest.config.ts
├── src/**/*.test.tsx
├── playwright.config.ts
├── e2e/
│   ├── auth.spec.ts
│   ├── patient-flow.spec.ts
│   └── portal.spec.ts
perf/
└── k6-smoke.js
```

## 5. Test Layer Responsibilities

**Unit (backend):** one route handler, mocked DB session — verifies validation, auth requirement, business logic branching.

**Integration (backend):** real Postgres via docker-compose, full request → ORM → DB path, verifies migrations work, constraints hold.

**Component (frontend):** single React component — renders, user interactions, API mocked via MSW (or fetch mock).

**E2E:** browser + full stack — verifies the seams between frontend and backend, including CORS, auth token propagation, portal QR flow.

**Security probes:** targeted negative tests — expired tokens, wrong-practitioner access, SQL injection strings, portal token brute-force resistance, CORS origin rejection.

**Performance:** baseline numbers — p50/p95 latency on auth login, patient list, portal check-in; bundle size budget; Lighthouse ≥80 on key pages.

## 6. Risk Matrix & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Portal token leakage | Med | Critical (PHI) | Dedicated security test suite for `/api/portal/{token}` |
| Demo user persists in prod | High | High | Deployment-readiness check flags `_ensure_demo_user()` |
| CORS misconfig exposes API | Med | High | Test that unlisted origins are rejected |
| Stripe webhook signature bypass | Low | Critical | Unit test for signature verification |
| Missing rate-limit on AI endpoints | High | Med (cost) | Flag in report; out of scope to fix |
| Alembic migration drift vs models | Med | High | Migration dry-run in deploy-readiness phase |
| Uploaded file path traversal | Low | High | Static code review on upload handlers |
| JWT secret weakness in dev | Low | Critical | Confirm `render.yaml` uses `generateValue: true` (already verified) |

## 7. Definition of Done

Before the final "GO" recommendation can be given:

- [x] Design spec written
- [ ] Implementation plan written
- [ ] Static analysis clean OR findings documented
- [ ] Backend test suite exists and runs
- [ ] Integration suite runs at least once against dockerized Postgres
- [ ] Frontend has at least a Vitest setup with smoke tests
- [ ] Playwright config + at least login + patient-portal E2E
- [ ] Docker builds succeed for both frontend and backend
- [ ] render.yaml validated
- [ ] Security review documents OWASP Top 10 posture
- [ ] Consolidated executive summary with GO/NO-GO/GO-WITH-CAVEATS
- [ ] All artifacts committed in a reviewable state (NOT auto-pushed)

## 8. What the User Will Receive

When you return from AFK you'll find:
1. A committable set of test files and config
2. A `docs/qa/reports/` folder with one report per phase
3. An executive summary with a one-page go/no-go
4. A list of any **production blockers** that require your decision before deploy
5. A `git status` showing all new files staged for your review (not committed by me)

## 9. Open Questions (left for user)

These won't block execution but I'll flag recommendations:

1. Should demo user be disabled in prod? (Currently auto-created on every startup — see `backend/app/main.py:19-42`)
2. CORS includes `localhost:3000` and `localhost:3747` — remove from prod list?
3. Is there a staging environment on Render, or is prod the first deploy?
4. HIPAA/BAA posture — does Render's free tier meet your compliance needs for PHI?
5. Rate limiting: should it be added before exposing AI endpoints publicly?
