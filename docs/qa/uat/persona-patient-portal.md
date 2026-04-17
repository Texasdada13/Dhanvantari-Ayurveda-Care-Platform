# UAT Script — Patient Portal Persona

**Persona:** Shuva (patient using portal for daily check-ins)
**Goal:** Access portal via QR code, view care plan, submit daily check-in
**Environment:** Production URL (e.g., https://dhanvantari.onrender.com/portal/{token})
**Auth:** None required — portal uses token-only access

---

## Pre-requisites
- [ ] A patient exists with an active care plan and portal token
- [ ] Portal token URL is accessible (from QR code or direct link)

---

## Journey Steps

### 1. Portal Access
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 1.1 | Scan QR code OR click portal link | Portal home page loads | |
| 1.2 | Verify patient name displayed | "Welcome, Shuva" or similar greeting | |
| 1.3 | Verify streak counter | Shows 0 or current streak | |
| 1.4 | Verify plan summary card | Shows plan title, supplement count, recipe count | |
| 1.5 | Verify next follow-up card | Shows date + reason (or "None scheduled") | |

### 2. View Care Plan
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 2.1 | Click "View Plan" | Full plan details page loads | |
| 2.2 | Verify supplements listed | Name, dose, timing, frequency, purpose visible | |
| 2.3 | Verify recipes listed | Name, meal slot, ingredients, instructions visible | |
| 2.4 | Verify lifestyle notes | Foods to avoid/include, breathing notes, nasal care | |
| 2.5 | Check plan duration | Start date + duration in weeks shown | |

### 3. Daily Check-in
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 3.1 | Click "Daily Check-in" | Check-in form loads | |
| 3.2 | Toggle morning habits | Warm water, breathing exercise, nasal oil checkboxes | |
| 3.3 | Toggle meal habits | Warm breakfast/lunch/dinner, avoided cold food, etc. | |
| 3.4 | Toggle supplement compliance | AM + PM supplements checkboxes | |
| 3.5 | Set symptom scores (1-5) | Digestion, urinary, sinus, energy sliders/selects | |
| 3.6 | Add notes (optional) | Free text field accepts input | |
| 3.7 | Submit check-in | Success message + habit completion % shown | |
| 3.8 | Try submitting again same day | Blocked: "Already checked in today" (409) | |

### 4. Check-in History
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 4.1 | Navigate to History | Last 90 days of check-ins listed | |
| 4.2 | Verify today's check-in appears | Today's entry at top with correct data | |
| 4.3 | Verify habit completion % | Calculated correctly based on toggled habits | |
| 4.4 | Verify symptom scores | Scores match what was submitted | |

### 5. Follow-ups
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 5.1 | Navigate to Follow-ups | Upcoming + past follow-ups listed | |
| 5.2 | Verify upcoming shows "days until" | Countdown accurate | |

### 6. Print Plan (from portal)
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 6.1 | Navigate to Print view | Printable plan layout renders | |
| 6.2 | Verify all sections present | Supplements, recipes, lifestyle | |
| 6.3 | Print or save as PDF | Clean A4 output | |

---

## Security Checks (embedded in UAT)
| Check | Expected | Pass? |
|-------|----------|-------|
| Access portal with invalid token | 404 — no data leaked | |
| Access portal with deactivated token | 404 | |
| Access patient API endpoints from portal (no Bearer token) | 401/403 | |
| Portal shows only this patient's data | No cross-patient data visible | |
| Portal URL does not expose patient IDs | Uses opaque token, not sequential ID | |

---

## Mobile Responsiveness
| Device | Expected | Pass? |
|--------|----------|-------|
| iPhone SE (375px) | Readable, touch-friendly, no horizontal scroll | |
| Galaxy S21 (360px) | Same | |
| iPad (768px) | Two-column layout or stacked cleanly | |

---

## Exit Criteria
- Portal loads within 5 seconds on first visit
- All check-in data persists correctly
- Streak counter updates after check-in
- History page reflects submitted check-ins
- Invalid tokens never expose patient data
- Works on mobile browsers (Chrome, Safari)
