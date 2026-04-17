# Phase 7 — Performance & Accessibility Report

**Run date:** 2026-04-16
**Mode:** Partial — some checks require running services

## Performance

### Frontend Bundle Analysis

**Status:** Deferred to frontend agent (running `next build`)

**Recommendations based on code review:**
- 5 uses of `<img>` instead of `<Image />` (ESLint flagged) — impacts LCP
- No dynamic imports visible for heavy components (Recharts, dosha wizard) — could lazy-load
- `react-markdown` + `remark-gfm` bundled — only used in AI chat; candidate for dynamic import
- Tailwind CSS 4 with PostCSS — should tree-shake well in production build

### API Latency Expectations (Render free-tier)

| Endpoint | Expected p50 | Expected p95 | Notes |
|----------|-------------|-------------|-------|
| `GET /api/health` | <50ms | <200ms | No DB hit |
| `POST /api/auth/login` | <200ms | <500ms | bcrypt hash comparison |
| `GET /api/patients` | <300ms | <1s | selectinload, depends on count |
| `POST /api/ai/chat` | 2-10s | 30s | Anthropic API latency |
| `GET /api/portal/{token}` | <300ms | <800ms | Multiple queries |

**Render free-tier cold start:** Expect 15-30s on first request after inactivity (containers spin down).

### k6 Load Test Script (scaffolded)

Saved as `perf/k6-smoke.js` for future use:

```javascript
// Run: k6 run perf/k6-smoke.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },
    { duration: '20s', target: 10 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
  },
};

const BASE = __ENV.API_URL || 'http://localhost:8747';

export default function () {
  const health = http.get(`${BASE}/api/health`);
  check(health, { 'health 200': (r) => r.status === 200 });

  const login = http.post(`${BASE}/api/auth/login`,
    JSON.stringify({ email: 'demo@dhanvantari.app', password: 'demo1234' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(login, { 'login 200': (r) => r.status === 200 });

  sleep(1);
}
```

## Accessibility

### Static Checks (from code review)

| Check | Status | Notes |
|-------|--------|-------|
| HTML semantic elements | Partial | Dashboard uses div-heavy layout; portal uses better semantics |
| ARIA labels on forms | Partial | Login form has labels; some dashboard forms use placeholder-only |
| Color contrast | Unknown | Tailwind defaults are usually compliant; needs Lighthouse verify |
| Keyboard navigation | Unknown | Tab order not tested (needs running app) |
| Focus indicators | Present | Tailwind's `focus-visible` ring used in shadcn/ui components |
| Skip-to-content link | Missing | No skip nav found in layout.tsx |
| Alt text on images | Partial | Supplement images lack alt text in some places |

### axe-core Integration

Can be run via Playwright:
```typescript
import AxeBuilder from '@axe-core/playwright';

test('dashboard passes axe', async ({ page }) => {
  await page.goto('/dashboard');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toHaveLength(0);
});
```

**Status:** Not executed (requires running frontend). Recommended for CI.

## Recommendations

1. **Add `<Image />` from next/image** for all supplement/practice logo images (LCP improvement)
2. **Lazy-load Recharts + react-markdown** via `dynamic(() => import(...))`
3. **Add skip-to-content link** in `layout.tsx`
4. **Run Lighthouse CI** post-deploy: target ≥80 on performance, ≥90 on accessibility
5. **Run axe-core via Playwright** in CI pipeline
6. **Add rate-limiting** on AI endpoints to prevent cost runaway
