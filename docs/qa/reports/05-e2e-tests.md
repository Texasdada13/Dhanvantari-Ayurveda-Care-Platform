# Phase 5 — E2E Test Report

**Run date:** 2026-04-16
**Framework:** Playwright (config + specs written, execution pending full stack)

## Summary

E2E tests were **scaffolded** but NOT executed because the full stack (frontend + backend + seeded DB) was not brought up together during this session. The test specs are ready to run when docker-compose is fully up.

## Test Specs Written

### `e2e/auth.spec.ts` — 4 tests
1. **Login page renders** — verifies email/password inputs visible
2. **Login with demo credentials** — full auth flow → dashboard redirect
3. **Bad credentials error** — error message shown, stays on login
4. **Unauthenticated redirect** — `/dashboard` → `/login`

### `e2e/portal.spec.ts` — 3 tests
1. **Portal home for valid token** — loads patient data
2. **Portal 404 for invalid token** — error state, no data leak
3. **Portal check-in form renders** — UI loads correctly

## How to Run

```bash
cd frontend

# Install Playwright + browser
npm i -D @playwright/test
npx playwright install chromium

# Start full stack
cd .. && docker compose up -d && docker compose --profile seed run seed

# Run E2E tests
cd frontend && npx playwright test

# View HTML report
npx playwright show-report
```

## Configuration

- **Config:** `frontend/playwright.config.ts`
- **Base URL:** `http://localhost:3747` (overridable: `PLAYWRIGHT_BASE_URL`)
- **API URL:** `http://localhost:8747` (overridable: `PLAYWRIGHT_API_URL`)
- **Browser:** Chromium
- **Screenshots:** on failure only
- **Traces:** on first retry

## Verdict

Tests are scaffolded and ready. **Execution requires running the full docker-compose stack.** Recommend adding Playwright to CI/CD pipeline with docker-compose as a service.
