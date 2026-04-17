# Phase 8 — Security & OWASP Top 10 Review

**Run date:** 2026-04-16
**Scope:** Full backend code review (4858 LoC) + bandit SAST + dependency CVEs
**Methodology:** OWASP Top 10 (2021) checklist against all 16 route files + core modules

## OWASP Top 10 Assessment

### A01 — Broken Access Control ⚠️ MEDIUM RISK

| Check | Status | Details |
|-------|--------|---------|
| All routes require auth | **PASS** | Every route uses `get_current_practitioner` or `require_active_subscription` — except portal (intentionally token-based) |
| Multi-tenant isolation | **PASS** | Patient queries filter by `practitioner_id == current.id` |
| IDOR protection | **PASS** | `_get_or_404` validates patient ownership before returning data |
| Portal token isolation | **PASS** | Token resolves to exactly one patient; tested + verified |
| Subscription enforcement | **PASS** | `require_active_subscription` checks trial + subscription status |
| Tier limits enforced | **PASS** | `check_patient_limit` on patient creation for Seed tier |

**Finding SEC-01 (Medium):** Some routes use `get_current_practitioner` (basic auth only) where `require_active_subscription` would be more appropriate:
- `pranayama.py`, `recipes.py`, `supplements.py`, `yoga.py`, `therapies.py` — a practitioner with expired trial + no subscription can still CRUD library items.
- **Impact:** Low (library items aren't patient PHI), but inconsistent with `patients.py` which requires active subscription.

### A02 — Cryptographic Failures ✅ LOW RISK

| Check | Status | Details |
|-------|--------|---------|
| Password hashing | **PASS** | `bcrypt.hashpw` with `gensalt()` — industry standard |
| JWT algorithm | **PASS** | HS256 — adequate for single-service deployment |
| JWT secret | **PASS** | `render.yaml` uses `generateValue: true`; default in config.py is insecure but only for dev |
| PHI encryption at rest | **N/A** | Postgres column-level encryption not used, but Render managed Postgres encrypts storage at rest |
| TLS in transit | **PASS** | Render provides HTTPS by default |

**Finding SEC-02 (Low):** JWT access tokens expire in **7 days** (`ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7`). This is very long for a health platform. Recommend: 1-4 hours for access tokens, keep 30-day refresh tokens.

### A03 — Injection ✅ LOW RISK

| Check | Status | Details |
|-------|--------|---------|
| SQL injection | **PASS** | All queries use SQLAlchemy ORM (parameterized). Zero raw SQL found across all 16 route files. |
| Search queries | **PASS** | `ilike` searches use f-strings for patterns (`f"%{q}%"`) — safe because SQLAlchemy parameterizes the whole expression |
| NoSQL injection | **N/A** | No NoSQL used |
| Command injection | **N/A** | No shell execution |
| XSS | **PASS** | API returns JSON only; frontend renders via React (auto-escapes). One exception: `consultation_notes.py` has `note_to_html()` — needs review for HTML injection if notes contain user input |

**Finding SEC-03 (Low):** `consultation_notes.py` converts notes to HTML for email. If patient-submitted data (check-in notes) flows into consultation notes that are then emailed, there's a potential stored XSS vector in the email body. Recommend: sanitize HTML output.

### A04 — Insecure Design ⚠️ MEDIUM RISK

**Finding SEC-04 (Medium):** Portal token entropy is adequate (`secrets.token_urlsafe()` → ~128 bits), BUT tokens are **never rotated** — once generated, a token is valid forever (as long as `active=True`). If a portal URL is shared or bookmarked on a shared device, there's no expiry.

**Finding SEC-05 (High):** **Demo user auto-created on every startup** (`backend/app/main.py:19-42`). In production on Render, this means `demo@dhanvantari.app` / `demo1234` is a valid login on the live site. This is a **production blocker**.

### A05 — Security Misconfiguration ⚠️ HIGH RISK

**Finding SEC-06 (High):** CORS allows `http://localhost:3000`, `http://localhost:3747` in production.

```python
# backend/app/main.py:68-73
allow_origins=[
    settings.FRONTEND_URL,
    "https://dhanvantari.patriottechsystems.com",
    "http://localhost:3000",   # ← REMOVE for production
    "http://localhost:3747",   # ← REMOVE for production
]
```

Impact: Any script running on `localhost:3000` or `localhost:3747` on any machine can make authenticated cross-origin requests to the production API.

**Finding SEC-07 (Medium):** `render.yaml` sets `DEBUG=false` (good), but `docs_url` and `redoc_url` are controlled by `settings.DEBUG`:
```python
docs_url="/api/docs" if settings.DEBUG else None
```
This is correct — Swagger UI disabled in prod. ✅

**Finding SEC-08 (Info):** No `TrustedHostMiddleware` is configured with specific hosts. The import exists but middleware is not added. This could allow host-header attacks.

### A06 — Vulnerable & Outdated Components 🔴 HIGH RISK

**12 Python CVEs across 5 packages** (from pip-audit):

| Package | CVEs | Severity | Fix |
|---------|------|----------|-----|
| `python-jose` 3.3.0 | 2 (PYSEC-2024-232/233) | **High** — JWT bypass | → 3.4.0 |
| `python-multipart` 0.0.12 | 3 (incl. CVE-2026-40347) | **High** — DoS, injection | → 0.0.26 |
| `starlette` 0.38.6 | 2 (CVE-2024-47874, CVE-2025-54121) | **High** — request smuggling | → 0.47.2 |
| `pillow` 10.4.0 | 2 (CVE-2026-25990, CVE-2026-40192) | Medium — image parsing | → 12.2.0 |
| `pytest` 8.3.3 | 1 (CVE-2025-71176) | Low (dev only) | → 9.0.3 |

**9 npm vulnerabilities** (4 high, 5 moderate) — most critical: Next.js 16.1.6 CSRF bypass.

**Verdict:** Both `python-jose` and Next.js CVEs are **production blockers**.

### A07 — Identification & Auth Failures 🔴 HIGH RISK

**Finding SEC-09 (High):** **No rate-limiting anywhere.** Login, registration, AI endpoints, and portal check-in have zero rate-limit protection.

- **Login brute-force:** Attacker can try unlimited passwords at API speed
- **Registration abuse:** Unlimited account creation
- **AI cost attack:** Unlimited calls to `POST /api/ai/chat` (each calls Anthropic API → $$$)
- **Portal enumeration:** Can probe portal tokens at high speed

**Recommendation:** Add `slowapi` or similar rate-limiter before production:
- Login: 5 attempts per minute per IP
- Registration: 3 per hour per IP
- AI: 10 per minute per user
- Portal: 30 per minute per IP

**Finding SEC-10 (Medium):** No account lockout mechanism after failed login attempts.

### A08 — Software & Data Integrity ✅ PASS

| Check | Status | Details |
|-------|--------|---------|
| Stripe webhook signature | **PASS** | `stripe.Webhook.construct_event(payload, signature, secret)` |
| Webhook rejects bad sig | **PASS** | Verified in test_billing.py |
| Webhook rejects missing sig | **PASS** | Returns 400/500 |

### A09 — Security Logging & Monitoring ⚠️ MEDIUM RISK

**Finding SEC-11 (Medium):** `echo=settings.DEBUG` on the DB engine logs all SQL queries when DEBUG=true. In production (DEBUG=false), this is fine. But there's **no application-level security logging** — failed logins, auth failures, webhook events are not logged.

**Finding SEC-12 (Low):** No structured logging. All output is `print()` statements in the seed script. No centralized log aggregation configured for Render.

### A10 — Server-Side Request Forgery (SSRF) ✅ LOW RISK

- `ai.py` calls Anthropic API via the official SDK — no user-controlled URLs
- `billing.py` calls Stripe via official SDK — no user-controlled URLs
- `consultation_notes.py` calls Resend via SDK — email address is from DB, not user-controlled
- No endpoints accept URLs from user input

## Severity Summary

| Severity | Count | IDs |
|----------|-------|-----|
| **Critical** | 0 | — |
| **High** | 4 | SEC-05 (demo user), SEC-06 (CORS localhost), SEC-09 (no rate-limit), A06 (CVEs) |
| **Medium** | 4 | SEC-01 (inconsistent auth), SEC-04 (portal no-expiry), SEC-10 (no lockout), SEC-11 (no security logging) |
| **Low** | 3 | SEC-02 (7-day JWT), SEC-03 (note HTML), SEC-12 (no structured logging) |
| **Info** | 1 | SEC-08 (TrustedHost) |

## Additional Findings from Deep Code Review (Agent)

### SEC-13 (CRITICAL): Cross-Tenant IDOR on Plan-Assignment Routes
**Files:** `therapies.py:360-458`, `yoga.py:331-436`, `pranayama.py:209-316`
**Impact:** Any authenticated practitioner can read/modify/delete therapy, yoga, and pranayama assignments on ANY plan — they only need to guess/enumerate plan IDs. No `practitioner_id` check is performed.
**Fix:** Join through `ConsultationPlan → Patient` and verify `Patient.practitioner_id == current.id`.

### SEC-14 (HIGH): Cross-Tenant IDOR on Supplement/Therapy Library Mutation
**Files:** `supplements.py:117-131`, `therapies.py:204-233`, `therapies.py:296-355`
**Impact:** Any authenticated practitioner can PATCH or DELETE another practitioner's supplements, therapies, and service packages. The queries filter by `id` alone without `practitioner_id`.
**Fix:** Add `.where(Model.practitioner_id == practitioner.id)` to all mutation queries.

### SEC-15 (MEDIUM): Plan Supplement/Recipe Deletion Has No Ownership Check
**File:** `plans.py:227-270`
**Impact:** DELETE endpoints for plan supplements and plan recipes accept a `ps_id`/`pr_id` without verifying the parent plan belongs to the calling practitioner.

### SEC-16 (CRITICAL): DEBUG=True by Default + SQL Echo Logs PHI
**Files:** `config.py:14` (`DEBUG: bool = True`), `database.py:17` (`echo=settings.DEBUG`)
**Impact:** If production env doesn't override DEBUG, ALL SQL queries (containing patient PHI) are logged to stdout → cloud log aggregation. Also exposes Swagger UI publicly.
**Fix:** Change default to `DEBUG: bool = False`.

### SEC-17 (LOW): Portal `notes` field has no max_length
**File:** `portal.py:58` — unbounded `str` field on unauthenticated endpoint
**Fix:** Add `Field(None, max_length=2000)` to `CheckInSubmit.notes`

### SEC-18 (LOW): PHI stored unencrypted at column level
**Impact:** Patient names, DOB, phone, email, lab values, clinical notes in plaintext Postgres columns. Render managed Postgres encrypts at rest, but column-level encryption adds defense-in-depth for HIPAA.

## Production Blockers (must fix)

1. **SEC-05:** Remove or gate `_ensure_demo_user()` — currently creates backdoor on every startup
2. **SEC-13:** Fix cross-tenant IDOR on plan-assignment routes (therapies, yoga, pranayama)
3. **SEC-14:** Fix cross-tenant IDOR on supplement/therapy library mutation
4. **SEC-16:** Change `DEBUG` default to `False`
5. **SEC-06:** Remove `localhost` origins from CORS
6. **SEC-09:** Add rate-limiting (at minimum on login + AI endpoints)
7. **A06:** Upgrade `python-jose`, `python-multipart`, `starlette`, `next` packages
