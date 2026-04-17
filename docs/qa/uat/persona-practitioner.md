# UAT Script — Practitioner Persona

**Persona:** Dr. Vaidya (BAMS practitioner, first-time user)
**Goal:** Complete first-day workflow from signup to sending a care plan to a patient
**Environment:** Production URL on Render (https://dhanvantari.onrender.com)

---

## Pre-requisites
- [ ] Frontend loads without console errors
- [ ] Backend health endpoint returns `{"status":"ok"}` at `/api/health`
- [ ] Demo credentials work: demo@dhanvantari.app / demo1234

---

## Journey Steps

### 1. Registration
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 1.1 | Navigate to `/register` | Registration form displayed | |
| 1.2 | Enter name, email, password, practice name, designation (BAMS) | All fields accept input | |
| 1.3 | Submit form | Redirected to dashboard, JWT stored, "trial" badge shown | |
| 1.4 | Try registering same email | Error "Email already registered" | |

### 2. Dashboard
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 2.1 | View dashboard | Stats cards show: 0 patients, 0 plans, 0 follow-ups | |
| 2.2 | Sidebar navigation loads | All links: Patients, Supplements, Recipes, Yoga, Pranayama, Services, Settings | |

### 3. Create Patient
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 3.1 | Click "New Patient" | Patient creation form opens | |
| 3.2 | Fill: first name, last name, DOB, sex, email | Accepts all fields | |
| 3.3 | Submit | Patient created, redirected to detail page | |
| 3.4 | Verify portal token generated | QR code / portal link visible | |
| 3.5 | Verify health profile created | Empty health profile section visible | |

### 4. Fill Health Profile
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 4.1 | Enter chief complaints | Text saved | |
| 4.2 | Enter dosha assessment (Vata-Pitta) | Dropdown accepts dosha type | |
| 4.3 | Enter lab values (cholesterol, HbA1c) | Numeric fields validated | |
| 4.4 | Save health profile | Success confirmation | |

### 5. Create Supplements & Recipes
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 5.1 | Navigate to Supplements | Library page loads | |
| 5.2 | Add supplement (e.g., Triphala) | Form accepts name, Sanskrit name, purpose | |
| 5.3 | Upload supplement image | Image preview shown | |
| 5.4 | Navigate to Recipes | Recipe page loads | |
| 5.5 | Create recipe with Ayurvedic properties | Rasa, Virya, Vipaka fields available | |

### 6. Create Care Plan
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 6.1 | Go to patient → Plans | Plan builder opens | |
| 6.2 | AI Draft: click "Draft Plan with AI" | Loading indicator, then plan populated | |
| 6.3 | Assign supplements (dose, timing, frequency) | Supplement assignments saved | |
| 6.4 | Assign recipes (meal slot) | Recipe assignments saved | |
| 6.5 | Assign yoga asanas | Yoga assignments saved | |
| 6.6 | Set plan title, duration, lifestyle notes | All fields editable | |
| 6.7 | Activate plan | Plan shows as active | |

### 7. Print & Share
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 7.1 | Click "Print Plan" | Print-optimized view opens | |
| 7.2 | Verify QR code on printout | QR code renders, pointing to portal URL | |
| 7.3 | Verify all plan sections in print view | Supplements, recipes, lifestyle notes visible | |

### 8. Dosha Assessment Wizard
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 8.1 | Navigate to patient → Dosha Assessment | Wizard launches | |
| 8.2 | Complete all assessment questions | Prakriti + Vikriti scored | |
| 8.3 | View radar chart | Dosha balance visualization renders | |
| 8.4 | Save assessment | Assessment stored in patient record | |

### 9. Consultation Notes
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 9.1 | Create new consultation note | Multi-section note form | |
| 9.2 | "Draft with AI" | AI generates structured note from patient data | |
| 9.3 | Edit and save note | Note persisted | |
| 9.4 | "Send to Patient" | Email sent (or queued) to patient | |

### 10. Billing
| Step | Action | Expected Result | Pass? |
|------|--------|----------------|-------|
| 10.1 | Navigate to Settings/Billing | Current plan shown (trial) | |
| 10.2 | Click "Upgrade" → Practice tier | Stripe checkout session opens | |
| 10.3 | Complete with test card 4242... | Subscription activated, tier updated | |
| 10.4 | Open Billing Portal | Stripe billing portal loads | |

---

## Exit Criteria
- All steps pass with no 500 errors
- Patient data persists across page refreshes
- AI features respond within 15 seconds
- Print view is usable on A4 paper
- Portal QR code resolves to working portal
