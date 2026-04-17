# Phase 9 — Accessibility Report

**Run date:** 2026-04-16
**Mode:** Static code review (runtime axe-core audit requires running frontend)

## Summary

Accessibility posture is **moderate** based on code review. Several gaps exist that should be addressed before production if the platform serves patients with disabilities.

## Findings

### Critical

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| A-01 | No skip-to-content link | `frontend/src/app/layout.tsx` | Screen reader users can't skip navigation |

### High

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| A-02 | Placeholder-only labels on some forms | Dashboard forms (patient create, supplement add) | Screen readers can't announce field purpose when placeholder clears |
| A-03 | Missing alt text on supplement images | `src/app/(dashboard)/supplements/page.tsx:63` | Images not described for screen reader users |
| A-04 | Missing alt text on practice logo | `src/app/(dashboard)/settings/page.tsx:157` | Same |

### Medium

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| A-05 | `<img>` instead of `<Image />` (5 places) | Multiple — see Phase 1 ESLint report | Missing loading="lazy", missing width/height for CLS |
| A-06 | Color-only indicators | Dashboard stat cards use colored icons to convey meaning | Colorblind users may miss status differences |
| A-07 | Radar chart (Recharts) no text alternative | `src/components/dosha-radar-chart.tsx` | Chart not accessible to screen readers without aria-label or description |

### Low / Info

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| A-08 | Focus ring visible (good) | shadcn/ui uses `focus-visible:ring` | Already handled |
| A-09 | Semantic HTML (partial) | Portal pages use semantic tags; dashboard is div-heavy | Minor navigation impact |
| A-10 | Tab order untested | Entire app | Needs runtime verification |

## Recommendations

1. **Add skip-to-content link** in `layout.tsx`:
   ```tsx
   <a href="#main" className="sr-only focus:not-sr-only">Skip to content</a>
   ...
   <main id="main">
   ```

2. **Convert placeholder-only fields to labeled inputs** — use `<Label>` from shadcn/ui

3. **Add `aria-label` to Recharts dosha radar chart** describing the data

4. **Add `alt` props to all `<img>` / `<Image>` tags** — especially supplement images and practice logos

5. **Run axe-core via Playwright** in CI after deploying:
   ```bash
   npm i -D @axe-core/playwright
   # Add to e2e tests (see Phase 5 report)
   ```

6. **Test keyboard navigation** end-to-end: Tab through login → dashboard → patient detail → portal

## WCAG 2.1 Compliance Assessment

| Level | Status | Notes |
|-------|--------|-------|
| A (minimum) | Partial | Missing: skip nav, text alternatives |
| AA (recommended) | Unknown | Color contrast untested, focus indicators present |
| AAA (enhanced) | Not targeted | Out of scope for initial launch |

## Verdict

Several WCAG Level A violations need addressing. For a health platform, accessibility is important for compliance (especially if any US healthcare entity is a client — ADA/Section 508). Recommend fixing Critical + High issues before production.
