# QA Report 04 -- Frontend Unit Tests

**Date:** 2026-04-16
**Stack:** Next.js 16.1.6 / React 19.2.3 / TypeScript 5 / Vitest 4.1.4

---

## 1. What Was Set Up

### Test tooling installed

| Package | Version | Purpose |
|---|---|---|
| `vitest` | ^4.1.4 | Test runner (Vite-native, ESM-first) |
| `@vitest/coverage-v8` | ^4.1.4 | Code coverage via V8 |
| `@testing-library/react` | ^16.3.2 | React component rendering helpers |
| `@testing-library/jest-dom` | ^6.9.1 | Custom DOM matchers (`toBeInTheDocument`, etc.) |
| `@testing-library/user-event` | ^14.6.1 | User interaction simulation |
| `jsdom` | ^29.0.2 | DOM environment for tests |

### Configuration files created

| File | Description |
|---|---|
| `vitest.config.ts` | Test environment (jsdom), setup files, `@/` path alias, v8 coverage, e2e exclusion |
| `vitest.setup.ts` | Imports `@testing-library/jest-dom/vitest` for DOM matchers |

### Scripts added to `package.json`

```json
"test": "vitest run",
"test:watch": "vitest",
"test:coverage": "vitest run --coverage"
```

---

## 2. Tests Written

### `src/lib/api/client.test.ts` -- API Client (8 tests)

- Verifies axios instance has correct `baseURL` (`http://localhost:8747`) and `Content-Type` header
- Validates all API namespace exports exist (`authApi`, `patientsApi`, `plansApi`, `portalApi`, etc. -- 24 namespaces)
- Tests request interceptor: attaches `Bearer` token from `localStorage` when present, omits it when absent
- Tests `supplementsApi.uploadImage` sends `FormData` with correct headers

### `src/components/dosha-radar-chart.test.tsx` -- Dosha Radar Chart (6 tests)

- Returns empty output when both `prakriti` and `vikriti` are `undefined` or `null`
- Renders chart wrapper `div.flex` when `prakriti` alone, `vikriti` alone, or both are provided
- Verifies chart wrapper has child elements (Recharts content)

### `src/app/(auth)/layout.test.tsx` -- Auth Layout (5 tests)

- Renders children correctly inside the layout
- Displays "Dhanvantari" brand name (desktop and mobile)
- Shows Charaka Samhita quotation
- Renders the Om symbol in brand logo
- Displays tagline: "Rooted in tradition. Powered by intelligence."

---

## 3. Test Results

```
 RUN  v4.1.4

 Test Files  3 passed (3)
      Tests  20 passed (20)
   Duration  4.08s
```

All 20 tests pass across 3 test files.

---

## 4. Build Results

```
next build -- Next.js 16.1.6 (Turbopack)

Compiled successfully in 7.2s
Generating static pages (17/17) in 546.1ms

Routes: 19 total (15 static, 4 dynamic)
```

Production build succeeds with no errors after fixes (see section 5).

---

## 5. Pre-Existing Issues Found and Fixed

The production build (`next build`) was broken before this work began due to several TypeScript errors. All were fixed during this session:

### 5.1 `playwright.config.ts` included in TypeScript compilation

**File:** `tsconfig.json`
**Problem:** The `include` pattern `**/*.ts` captured `playwright.config.ts` and `e2e/*.spec.ts`, which import `@playwright/test` (not installed as a dependency).
**Fix:** Added `"e2e"` and `"playwright.config.ts"` to the `exclude` array.

### 5.2 Missing `"outline"` Badge variant

**File:** `src/components/ui/badge.tsx`
**Problem:** `BadgeVariant` type did not include `"outline"`, but `src/app/(dashboard)/intake/page.tsx` used `variant="outline"`.
**Fix:** Added `"outline"` to the `BadgeVariant` union type and added `outline: "bg-transparent text-foreground border-border"` to the variants record.

### 5.3 Missing `onEdit` prop on `SortableAssignmentList`

**File:** `src/components/sortable-assignment-list.tsx`
**Problem:** `onEdit` was required in `SortableAssignmentListProps`, but `src/app/(dashboard)/patients/[id]/page.tsx` omitted it for the therapies list.
**Fix:** Made `onEdit` optional (`onEdit?: ...`) in the props interface, `SortableCard`, and `ContextMenu`. Conditionally renders the Edit button only when `onEdit` is provided.

### 5.4 `unknown` type used as `ReactNode` in portal print page

**File:** `src/app/portal/[token]/plan/print/page.tsx`
**Problem:** Expressions like `{s.name_sanskrit && <span>...</span>}` fail in React 19 strict mode because `unknown && JSX` can resolve to `unknown`, which is not assignable to `ReactNode`.
**Fix:** Changed all `unknown && (JSX)` patterns to ternary form: `unknown ? (JSX) : null`.

---

## 6. Coverage Gaps

| Area | Status | Notes |
|------|--------|-------|
| API client | Tested | Interceptors, auth headers, exports |
| Dosha radar chart | Tested | Rendering, null handling |
| Auth layout | Tested | Children rendering, branding |
| Dashboard pages | Gap | Complex; depend on API data |
| Portal pages | Gap | Need MSW for API mocking |
| Plan builder | Gap | Complex state management |
| Video player | Gap | Browser API dependencies |

---

## 7. How to Run

```bash
cd frontend
npm run test           # single run
npm run test:watch     # watch mode
npm run test:coverage  # with v8 coverage report
```

---

## 8. Summary

| Metric | Value |
|---|---|
| Test files | 3 |
| Tests | 20 |
| Passing | 20 (100%) |
| Failing | 0 |
| Build status | Passing |
| Pre-existing TS errors fixed | 4 |
| New dev dependencies added | 6 |

Frontend test infrastructure is fully operational. 20 tests pass covering API client configuration, component rendering, and layout structure. Four pre-existing TypeScript errors that blocked the production build were discovered and fixed. Recommend expanding coverage to dashboard components using MSW for API mocking in future iterations.
