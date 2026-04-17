# Phase 1 — Static Analysis Report

**Run date:** 2026-04-16
**Mode:** autonomous

## Summary

| Scan | Tool | Findings | Severity |
|------|------|----------|----------|
| Frontend lint | ESLint 9 (Next 16) | 5 errors, 15 warnings | Med |
| Frontend types | tsc --noEmit | 13 errors | **High** |
| Frontend deps | npm audit | 9 vulns (4 high, 5 mod) | **High** |
| Backend lint | ruff | 41 errors | Low–Med |
| Backend deps | pip-audit | 12 CVEs in 5 packages | **High** |
| Backend SAST | bandit | 0 issues | — |
| Secret scan | grep patterns | 0 real leaks | — |

## 1.1 Frontend ESLint — 5 errors, 15 warnings

### Errors (must fix)

| File:Line | Rule | Issue |
|-----------|------|-------|
| `src/app/(auth)/layout.tsx:15` | `react/no-unescaped-entities` | Unescaped `"` — 2 instances |
| `src/app/(dashboard)/dashboard/page.tsx:48` | `react-hooks/purity` | `Date.now()` called during render |
| `src/app/(dashboard)/layout.tsx:48` | `react-hooks/set-state-in-effect` | `setState` called directly in effect body |
| `src/app/(dashboard)/patients/page.tsx:71` | `react-hooks/purity` | `Date.now()` called during render (in `calcAge`) |

### Warnings (advisory)

- 10x unused imports (`@typescript-eslint/no-unused-vars`)
- 5x `<img>` usage instead of `next/image` (perf + LCP)

**Assessment:** React 19 purity warnings are real — `Date.now()` in render causes hydration mismatches. Impure calls should be wrapped in `useMemo` with stable dep or calculated in a `useEffect`.

## 1.2 TypeScript — 13 errors (tsc --noEmit)

```
src/app/(dashboard)/intake/page.tsx(142,20)     Badge variant "outline" not in BadgeVariant
src/app/(dashboard)/intake/page.tsx(242,22)     Badge variant "outline" not in BadgeVariant
src/app/(dashboard)/patients/[id]/page.tsx(1154,20)  SortableAssignmentList missing required `onEdit` prop
src/app/(dashboard)/services/page.tsx  (6 instances)  Badge variant "outline" not in BadgeVariant
src/app/portal/[token]/plan/print/page.tsx (4 instances) `unknown` not assignable to ReactNode
```

**Impact:** Build will fail on `next build` with strict settings. This is a **production blocker** unless tsconfig relaxes strict checks.

**Recommendation:**
- Extend the `BadgeVariant` type to include `"outline"` OR change call sites to an existing variant
- Add `onEdit` to `SortableAssignmentList` caller OR make prop optional in the interface
- Cast / type-guard the unknown values in the portal print page

## 1.3 npm audit — 9 vulnerabilities

| Package | Severity | CVE topic |
|---------|----------|-----------|
| `next` 16.0.0–16.2.2 | **high** | HTTP request smuggling, Server Actions CSRF bypass, DoS |
| `path-to-regexp` | high | ReDoS |
| `picomatch` | high | ReDoS |
| `flatted` | high | Prototype pollution |
| `hono` | moderate | 6 advisories incl. path traversal |
| `follow-redirects` | moderate | Auth-header leak on cross-domain redirect |

**Blocker:** Next.js 16.0.0–16.2.2 has high-severity advisories including **null-origin Server Actions CSRF bypass** (GHSA-mq59-m269-xvcx). Platform uses `next@16.1.6`.

**Fix:** `npm audit fix --force` (upgrades Next to 16.2.4+). Test after upgrade.

## 1.4 Backend ruff — 41 errors

```
28 × F401  [*] unused-import        (auto-fixable)
10 × E712      true-false-comparison (== True / == False)
 2 × F841      unused-variable
 1 × F821  !!  undefined-name        ← 'VideoReference' in app/models/pranayama.py:30
```

**Note:** `F821 undefined-name` is potentially a real bug — forward reference to `VideoReference` model. Needs manual verification that the string reference resolves at runtime (it may work via SQLAlchemy string-based relationship evaluation).

## 1.5 pip-audit — 12 CVEs in 5 packages

| Package | Current | Fix | Severity |
|---------|---------|-----|----------|
| `python-jose` 3.3.0 | `3.4.0` | **High** (PYSEC-2024-232/233) — JWT handling |
| `python-multipart` 0.0.12 | `0.0.26` | High (CVE-2024-53981, CVE-2026-24486, CVE-2026-40347) |
| `pillow` 10.4.0 | `12.2.0` | Med (CVE-2026-25990, CVE-2026-40192) |
| `starlette` 0.38.6 | `0.47.2` | High (CVE-2024-47874, CVE-2025-54121) |
| `pytest` 8.3.3 | `9.0.3` | Low (dev-only) |

**Blocker:** `python-jose` CVE affects JWT verification — this is the auth layer. Upgrade required.

## 1.6 bandit — 0 issues

4858 LoC scanned, no security issues detected at any severity. Good.

## 1.7 Secret scan — clean

`grep` for `sk-ant-`, `sk_live_`, `sk_test_`, AWS keys, PEM headers, GitHub tokens, hardcoded passwords:
- Only hit: comment in `README.md:58` documenting env var pattern (not a real secret)

No `.env` files committed. Good.

## Production Blockers (must fix before deploy)

1. **TypeScript build will fail** — 13 errors must be resolved or tsconfig adjusted
2. **python-jose CVE on JWT layer** — bump to 3.4.0
3. **Next.js CSRF bypass vulnerability** — bump to 16.2.4+
4. **starlette CVE** — auto-updated when FastAPI upgrades; verify dependency graph

## Recommended Fixes (non-blocking but advised)

- Run `npm audit fix` for moderate vulns
- Run `ruff check app/ --fix` for 28 auto-fixable imports
- Refactor `Date.now()` out of render (React 19 purity)
- Move `<img>` → `<Image />` for LCP improvements

## Artifacts

- `docs/qa/reports/_npm-audit.json` — full npm audit JSON
- Raw lint/typecheck output captured in session log
