"""
Demo seed — creates a demo practitioner account with one fully loaded patient
(Shuva Mukhopadhyay) including care plan, supplements, recipes, 21 days of
check-in history, and a scheduled follow-up.

Run from backend/: python scripts/seed_demo.py
"""
import asyncio
import random
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt as _bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.models.practitioner import Practitioner, SubscriptionTier
from app.models.patient import Patient, HealthProfile
from app.models.checkin import CheckInToken, DailyCheckIn
from app.models.plan import ConsultationPlan, Supplement, PlanSupplement, Recipe, PlanRecipe
from app.models.followup import FollowUp

DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def hash_password(pw: str) -> str:
    return _bcrypt.hashpw(pw.encode(), _bcrypt.gensalt()).decode()

DEMO_EMAIL    = "demo@dhanvantari.app"
DEMO_PASSWORD = "demo1234"


# ── Supplement data for Shuva's plan ────────────────────────────────────────

SHUVA_SUPPLEMENTS = [
    {
        "name": "Avipattikar Churna",
        "name_sanskrit": "Avipattikar Churna (Dhootpapeshwar)",
        "category": "Digestive",
        "purpose": "Supports digestion, reduces acid reflux and gut inflammation. Classical formula for Pitta in the digestive tract.",
        "dosha_effect": "Reduces Pitta, balances Kapha",
        "typical_dose": "½ tsp twice daily with water before meals",
        "cautions": "Avoid in excess during pregnancy. Monitor for loose stools in high doses.",
        "is_classical": True,
    },
    {
        "name": "Haridrakhandam",
        "name_sanskrit": "Haridrakhandam (Kottakkal)",
        "category": "Anti-inflammatory",
        "purpose": "Anti-inflammatory, supports respiratory and skin health, reduces allergic load. Turmeric-based classical formula.",
        "dosha_effect": "Reduces Kapha and Pitta, mildly increases Vata",
        "typical_dose": "¼ tsp twice daily with water after meals",
        "cautions": "Avoid in high Vata without ghee or milk. Not recommended in high doses during pregnancy.",
        "is_classical": True,
    },
    {
        "name": "Vyoshadi Vatkam",
        "name_sanskrit": "Vyoshadi Vatkam (Kottakkal)",
        "category": "Respiratory",
        "purpose": "Supports respiratory tract and digestion. Classical Kerala tablet for Kapha in the lungs, sinus congestion, and breathing difficulty.",
        "dosha_effect": "Reduces Kapha and Vata in respiratory tract",
        "typical_dose": "¼ tsp (or 2 tablets) twice daily with water after meals",
        "cautions": "Use cautiously in high Pitta conditions. Contains pippali (long pepper).",
        "is_classical": True,
    },
    {
        "name": "Neeri Tablets",
        "name_sanskrit": "Neeri (Aimil Pharmaceuticals)",
        "category": "Urinary",
        "purpose": "Urinary tract support — reduces UTI frequency, supports bladder health and kidney function. Contains Gokshura, Punarnava, Varuna.",
        "dosha_effect": "Reduces Vata and Pitta in urinary tract",
        "typical_dose": "1 tablet twice daily with water after meals",
        "cautions": "Generally safe. Consult if on diuretic medications.",
        "is_classical": False,
    },
]

SHUVA_RECIPES = [
    {
        "name": "Warm Oat Bowl (Shuva's Breakfast)",
        "meal_type": "Breakfast",
        "dosha_good_for": "Vata, Pitta",
        "dosha_avoid": "Kapha (reduce milk/sweetener)",
        "ingredients": "½ cup oats, 1 cup water or milk, chopped figs, 1 date, 6–8 almonds, 1 Brazil nut",
        "instructions": "Add oats and water (or milk) to a saucepan. Cook on low heat for 5–7 minutes. Add chopped figs, date pieces, almonds, and Brazil nuts. Serve warm.",
        "notes": "Provides steady energy and supports digestion. The nuts add healthy fat and Ojas. Best eaten within 1 hour of waking.",
        "is_tea": False,
    },
    {
        "name": "Savory Vegetable Oats",
        "meal_type": "Breakfast",
        "dosha_good_for": "Vata, Kapha",
        "dosha_avoid": None,
        "ingredients": "½ cup oats, 1 cup water, chopped carrots, zucchini or spinach, pinch turmeric, pinch cumin, salt to taste",
        "instructions": "Heat pan with a little oil or ghee. Add cumin and turmeric. Add chopped vegetables and sauté lightly. Add oats and water. Cook until soft (5–6 minutes).",
        "notes": "Savory breakfast alternative — good for those who prefer less sweet food in the morning. Lighter than the sweet oat bowl.",
        "is_tea": False,
    },
    {
        "name": "Barley Vegetable Bowl",
        "meal_type": "Lunch",
        "dosha_good_for": "Kapha, Pitta",
        "dosha_avoid": "High Vata (add more ghee)",
        "ingredients": "½ cup barley, carrots, green beans, zucchini, turmeric, cumin, ginger, salt",
        "instructions": "Cook barley in water until soft. In a separate pan, sauté cumin and ginger. Add chopped vegetables and cook until soft. Mix cooked barley and vegetables together. Add salt and turmeric. Serve warm.",
        "notes": "Barley is the recommended grain for Shuva — lighter than rice, reduces Kapha, supports urinary tract health. Best as main meal.",
        "is_tea": False,
    },
    {
        "name": "Light Chicken Vegetable Soup",
        "meal_type": "Lunch",
        "dosha_good_for": "Vata, Kapha",
        "dosha_avoid": None,
        "ingredients": "Chicken pieces (marinated), carrots, zucchini, ginger, turmeric, cumin, salt, water",
        "instructions": "Marinate chicken with spices beforehand. Add chicken and vegetables to pot. Add water, ginger, cumin, and turmeric. Simmer for 20–25 minutes. Serve warm.",
        "notes": "Marinating the chicken is essential — improves digestibility. Light and nourishing. Can be used as both lunch and a lighter dinner.",
        "is_tea": False,
    },
    {
        "name": "Simple Fish with Vegetables",
        "meal_type": "Lunch",
        "dosha_good_for": "Vata, Pitta",
        "dosha_avoid": None,
        "ingredients": "Fish fillet, zucchini or asparagus, turmeric, coriander powder, ginger, olive oil or ghee",
        "instructions": "Marinate fish with turmeric, coriander, and ginger. Cook fish in a pan with a little oil. Sauté vegetables separately. Serve together with barley or rice.",
        "notes": "Fresh fish is preferred. Marinating with turmeric reduces Ama and improves digestibility. White fish is lighter for the gut.",
        "is_tea": False,
    },
    {
        "name": "Coriander-Barley Tea",
        "meal_type": "Drink",
        "dosha_good_for": "Pitta, Kapha, Vata",
        "dosha_avoid": None,
        "ingredients": "1 tsp coarsely ground barley, 1 tsp coriander seeds (daniya), 2 cups water",
        "instructions": "Coarsely grind barley and coriander seeds together. Boil 1 teaspoon of mixture in water for several minutes. Strain and drink warm.",
        "notes": "Prescribed specifically for Shuva's urinary tract issues. Drink 2–3 times daily. Coriander is cooling and soothing for the bladder; barley is a classical Ayurvedic diuretic.",
        "is_tea": True,
    },
    {
        "name": "Licorice Tea",
        "meal_type": "Drink",
        "dosha_good_for": "Vata, Pitta",
        "dosha_avoid": "Kapha (limit frequency)",
        "ingredients": "Licorice root (mulethi) or licorice tea bag, hot water",
        "instructions": "Steep licorice root or tea bag in hot water for 3–5 minutes. Drink warm.",
        "notes": "Soothes respiratory and digestive irritation. Particularly useful for Shuva's acid reflux and ear/sinus congestion. Rotate with Tulsi and Coriander-Barley teas.",
        "is_tea": True,
    },
]


async def get_or_create_supplement(db: AsyncSession, data: dict) -> Supplement:
    result = await db.execute(select(Supplement).where(Supplement.name == data["name"]))
    s = result.scalars().first()
    if not s:
        s = Supplement(**data)
        db.add(s)
        await db.flush()
    return s


async def get_or_create_recipe(db: AsyncSession, data: dict) -> Recipe:
    result = await db.execute(select(Recipe).where(Recipe.name == data["name"]))
    r = result.scalars().first()
    if not r:
        r = Recipe(**data)
        db.add(r)
        await db.flush()
    return r


async def seed_demo():
    async with AsyncSessionLocal() as db:
        # ── 1. Demo practitioner ─────────────────────────────────────────────
        result = await db.execute(select(Practitioner).where(Practitioner.email == DEMO_EMAIL))
        practitioner = result.scalars().first()
        if not practitioner:
            practitioner = Practitioner(
                name="Meenakshi Sharma",
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                practice_name="Meenakshi Ayurveda",
                designation="Vaidya, BAMS",
                bio="Classical Ayurvedic practitioner specialising in chronic disease management, digestive health, and respiratory conditions. 12 years of clinical experience.",
                subscription_tier=SubscriptionTier.PRACTICE,
                subscription_active=True,
                email_verified=True,
            )
            db.add(practitioner)
            await db.flush()
            print(f"Created demo practitioner: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print(f"Demo practitioner already exists: {DEMO_EMAIL}")

        # ── 2. Patient: Shuva Mukhopadhyay ──────────────────────────────────
        result = await db.execute(
            select(Patient).where(
                Patient.practitioner_id == practitioner.id,
                Patient.first_name == "Shuva",
                Patient.last_name == "Mukhopadhyay",
            )
        )
        patient = result.scalars().first()

        if not patient:
            patient = Patient(
                practitioner_id=practitioner.id,
                first_name="Shuva",
                last_name="Mukhopadhyay",
                dob=date(1984, 4, 23),
                sex="M",
                location="Ocala, Florida",
                occupation="High-stress work environment (long hours)",
                weight_lbs=175.0,
                exercise_notes="Weight lifting ~4x/week, abdominal exercises ~3x/week. Limited cardiovascular activity currently.",
                diet_pattern="Primarily non-vegetarian (chicken, fish, shrimp daily). Occasional vegetarian meals. Inconsistent meal timing. Nighttime snacking.",
                sleep_notes="Irregular sleep schedule. Work stress disrupts sleep rhythm.",
                stress_level="HIGH",
            )
            db.add(patient)
            await db.flush()
            print(f"Created patient: {patient.first_name} {patient.last_name} (id={patient.id})")

            # ── Health profile ────────────────────────────────────────────
            hp = HealthProfile(
                patient_id=patient.id,
                # Ayurvedic
                dosha_primary="Kapha-Vata",
                dosha_secondary="Pitta",
                dosha_imbalances="Kapha accumulation in respiratory and sinus channels. Vata disturbance in urinary tract and nervous system. Agni imbalance contributing to gut inflammation.",
                agni_assessment="Vishama Agni (irregular digestive fire) — intermittent bloating, reflux, and variable appetite.",
                ama_assessment="Moderate — gut inflammation, reflux, and post-meal heaviness suggest Ama accumulation in GI tract.",
                prakriti_notes="Kapha-Vata prakriti. Kapha provides strong physical constitution and endurance; Vata brings intensity and creativity under stress.",
                vikriti_notes="Current imbalance: Kapha elevated in upper respiratory tract and sinuses; Vata aggravated in urinary tract due to past trauma and irregular lifestyle. Secondary Pitta elevation from high-stress work.",
                # Clinical
                chief_complaints=(
                    "1. Chronic ear infections associated with partially perforated eardrums.\n"
                    "2. Recurrent urinary issues — frequent urination and sensation of incomplete bladder emptying.\n"
                    "3. History of urethral injury from childhood sports contributing to ongoing urinary symptoms.\n"
                    "4. Recurrent bladder infections.\n"
                    "5. Digestive discomfort including gut inflammation, occasional acid reflux, and abdominal swelling after long work hours.\n"
                    "6. Sinus congestion leading to ear infections.\n"
                    "7. Allergies, asthma, and breathing difficulty.\n"
                    "8. Fatigue and body inflammation after prolonged work periods."
                ),
                medical_history=(
                    "Childhood urethral stricture with surgical intervention following football injury. "
                    "Recurrent urinary tract infections. Chronic ear infections due to eardrum perforation. "
                    "Allergies and respiratory congestion. Currently on Vyvanse. Recent weight reduction of ~20 lbs."
                ),
                current_medications="Vyvanse (ADHD medication)",
                allergies="Reported allergic tendencies — elevated eosinophils at 10.3% suggesting allergic or inflammatory response.",
                # Labs
                cholesterol_total=184.0,
                hdl=54.0,
                ldl=116.0,
                hemoglobin=16.4,
                hematocrit=50.5,
                eosinophils_pct=10.3,
                glucose=89.0,
                hba1c=5.5,
                testosterone=1608.0,
                tsh=2.94,
                psa=1.05,
                creatinine=1.27,
                egfr=73.0,
                lab_date=date(2025, 3, 1),
                lab_notes=(
                    "LDL mildly elevated (116, optimal <100). Eosinophils elevated at 10.3% — correlates with allergic/inflammatory load. "
                    "Testosterone elevated at 1608 ng/dL — monitor. Hematocrit 50.5% upper normal. "
                    "Kidney function adequate (eGFR 73). All other markers within normal range."
                ),
                # Ashtavidha
                nadi_notes="Kapha-Vata nadi — slow and irregular pattern. Occasional Pitta surges during stress.",
                jihwa_notes="Moderate white coating on tongue — indicates Ama in GI tract. Slightly swollen edges.",
                mutra_notes="Frequent urination, incomplete emptying sensation. History of structural injury (urethral stricture).",
                mala_notes="Inconsistent bowel movements. Occasional constipation followed by loose stools — Vishama pattern.",
            )
            db.add(hp)
            await db.flush()

            # ── Check-in token ────────────────────────────────────────────
            tok = CheckInToken(patient_id=patient.id)
            db.add(tok)
            await db.flush()

        else:
            print(f"Patient Shuva already exists (id={patient.id}), skipping recreation.")
            hp = patient.health_profile
            tok = patient.checkin_token

        # ── 3. Supplements ───────────────────────────────────────────────────
        supp_objects = []
        for s_data in SHUVA_SUPPLEMENTS:
            s = await get_or_create_supplement(db, s_data)
            supp_objects.append(s)
            print(f"  Supplement: {s.name}")

        # ── 4. Recipes ───────────────────────────────────────────────────────
        # Also add Tulsi Tea from library if not already there
        tulsi_result = await db.execute(select(Recipe).where(Recipe.name.ilike("%tulsi%")))
        tulsi = tulsi_result.scalars().first()

        recipe_objects = []
        for r_data in SHUVA_RECIPES:
            r = await get_or_create_recipe(db, r_data)
            recipe_objects.append(r)
            print(f"  Recipe: {r.name}")
        if tulsi:
            recipe_objects.insert(0, tulsi)

        # ── 5. Care plan ─────────────────────────────────────────────────────
        result = await db.execute(
            select(ConsultationPlan).where(
                ConsultationPlan.patient_id == patient.id,
                ConsultationPlan.active == True,
            )
        )
        plan = result.scalars().first()

        if not plan:
            plan_start = date.today() - timedelta(days=21)
            plan = ConsultationPlan(
                patient_id=patient.id,
                title="Initial Protocol — Shuva",
                active=True,
                duration_weeks=3,
                start_date=plan_start,
                foods_to_include=(
                    "Warm cooked meals as primary diet. Barley as main grain where possible. "
                    "Cooked vegetables with moderate spices. Well-prepared chicken or fish (always marinated). "
                    "Warm breakfast daily within 1 hour of waking.\n\n"
                    "Recommended vegetables: zucchini, bottle gourd (lauki), ridge gourd, carrots, "
                    "green beans, spinach, asparagus, cabbage, pumpkin, sweet potato (small quantity). "
                    "Cook or sauté — avoid raw salads while digestion is inflamed.\n\n"
                    "Recommended spices: cumin, coriander, turmeric, ginger. "
                    "Nuts: almonds (6–8), Brazil nut (1) for breakfast. Dried fruit: figs, dates (in moderation)."
                ),
                foods_to_avoid=(
                    "Yogurt — aggravates Kapha and digestive inflammation.\n"
                    "Fermented foods (kimchi, etc.) — aggravates mucus accumulation.\n"
                    "Cold or refrigerated foods — disrupts digestive warmth (Agni).\n"
                    "Beetroot juice — excess sugar spike.\n"
                    "Excess sugar from juices and sweets.\n"
                    "Cold beverages during meals.\n"
                    "Large amounts of raw salads while gut is inflamed.\n"
                    "Late-night heavy meals — no snacking after 8pm."
                ),
                lifestyle_notes=(
                    "Maintain regular meal timing — eat at consistent times each day. "
                    "Avoid late-night snacking. Finish dinner before 8pm.\n\n"
                    "Continue strength training (4x/week). ADD cardiovascular activity: "
                    "brisk walking or light jogging 3–4 times per week.\n\n"
                    "Aim for consistent sleep schedule — same wake time daily. "
                    "Reduce caffeine and nicotine during heavy work periods when possible.\n\n"
                    "For daughter's respiratory symptoms: pinch of pippali (long pepper) powder "
                    "mixed in milk, ghee, or honey once or twice daily."
                ),
                breathing_notes=(
                    "Morning breathing practice — 5 to 10 minutes daily:\n"
                    "1. Sit comfortably, spine upright.\n"
                    "2. Slow nasal breathing only.\n"
                    "3. Inhale for 4 seconds.\n"
                    "4. Exhale for 6 seconds.\n"
                    "5. Continue for 5–10 minutes.\n\n"
                    "This helps regulate nervous system tone, supports the parasympathetic response, "
                    "and improves respiratory function over time."
                ),
                nasal_care_notes=(
                    "Daily nasal lubrication (Nasya) — each morning:\n"
                    "Apply 1–2 drops of warm sesame oil or ghee in each nostril.\n"
                    "Best done after morning breathing practice while still sitting.\n\n"
                    "Benefits: reduces nasal dryness, soothes irritated mucous membranes, "
                    "supports sinus comfort, and may reduce frequency of ear infections over time."
                ),
                followup_notes=(
                    "Follow this plan for 2–3 weeks. Monitor and report:\n"
                    "• Digestion — reflux, bloating, regularity\n"
                    "• Urinary symptoms — frequency, incomplete emptying, any discomfort\n"
                    "• Sinus and respiratory symptoms — congestion, ear discomfort, breathing\n"
                    "• Overall energy levels\n\n"
                    "We will reassess and adjust the protocol based on how your body responds. "
                    "WhatsApp Meenakshi with any questions or significant changes."
                ),
            )
            db.add(plan)
            await db.flush()
            print(f"Created care plan: {plan.title}")

            # Supplement dosing details
            supp_dosing = [
                {"dose": "½ tsp",    "timing": "Before meals",  "frequency": "Twice daily", "special_notes": "Take with warm water. Classical digestive formula — take consistently."},
                {"dose": "¼ tsp",    "timing": "After meals",   "frequency": "Twice daily", "special_notes": "Anti-inflammatory support. Take with warm water after eating."},
                {"dose": "¼ tsp",    "timing": "After meals",   "frequency": "Twice daily", "special_notes": "Respiratory tract support. Take with warm water after eating."},
                {"dose": "1 tablet", "timing": "After meals",   "frequency": "Twice daily", "special_notes": "Urinary tract support. Take with warm water after meals."},
            ]
            for supp, dosing in zip(supp_objects, supp_dosing):
                ps = PlanSupplement(plan_id=plan.id, supplement_id=supp.id, **dosing)
                db.add(ps)

            # Recipes with meal slots
            recipe_slots = [
                ("Breakfast Option 1", tulsi if tulsi else None),
                ("Breakfast Option 2", None),
                ("Breakfast Option 3", None),
                ("Main Lunch", None),
                ("Lunch / Dinner", None),
                ("Lunch", None),
                ("Morning & Afternoon", None),
                ("Rotate Daily", None),
            ]
            for recipe, slot_info in zip(recipe_objects[:8], recipe_slots):
                slot = slot_info[0]
                pr = PlanRecipe(plan_id=plan.id, recipe_id=recipe.id, meal_slot=slot)
                db.add(pr)

            await db.flush()
            print(f"Added {len(supp_objects)} supplements and {min(len(recipe_objects), 8)} recipes to plan")
        else:
            print("Care plan already exists, skipping.")

        # ── 6. 21 days of check-in history ───────────────────────────────────
        result = await db.execute(
            select(DailyCheckIn).where(DailyCheckIn.patient_id == patient.id)
        )
        existing_checkins = result.scalars().all()

        if not existing_checkins:
            print("Creating 21 days of check-in history...")
            token_result = await db.execute(
                select(CheckInToken).where(CheckInToken.patient_id == patient.id)
            )
            token_obj = token_result.scalars().first()

            today = date.today()
            for i in range(21, 0, -1):
                checkin_date = today - timedelta(days=i)
                week = (21 - i) // 7  # 0, 1, 2

                # Compliance improves week over week
                base_compliance = [0.55, 0.72, 0.85][week]

                def yn(prob: float) -> bool:
                    return random.random() < prob

                # Symptom scores improve over time (1=worst, 5=best)
                def score(base: float, noise: float = 0.8) -> int:
                    raw = base + random.uniform(-noise, noise)
                    return max(1, min(5, round(raw)))

                week_scores = [
                    {"digestion": 2.2, "urinary": 1.8, "sinus": 2.0, "energy": 2.0},
                    {"digestion": 3.0, "urinary": 2.5, "sinus": 2.8, "energy": 2.8},
                    {"digestion": 3.8, "urinary": 3.2, "sinus": 3.5, "energy": 3.7},
                ][week]

                # Skip ~2 days randomly over the 3 weeks (no check-in)
                if random.random() < 0.09:
                    continue

                ci = DailyCheckIn(
                    patient_id=patient.id,
                    date=checkin_date,
                    # Morning
                    warm_water=yn(base_compliance + 0.15),
                    breathing_exercise=yn(base_compliance - 0.1),
                    nasal_oil=yn(base_compliance - 0.2),
                    # Breakfast
                    warm_breakfast=yn(base_compliance + 0.1),
                    avoided_cold_food=yn(base_compliance + 0.05),
                    avoided_yogurt=yn(base_compliance + 0.1),
                    # Herbal tea
                    herbal_tea_am=yn(base_compliance + 0.05),
                    # Lunch
                    warm_lunch=yn(base_compliance + 0.1),
                    included_barley=yn(base_compliance - 0.05),
                    no_cold_drinks=yn(base_compliance + 0.1),
                    # Dinner
                    warm_dinner=yn(base_compliance),
                    dinner_before_8pm=yn(base_compliance - 0.1),
                    # Supplements
                    supplements_am=yn(base_compliance + 0.1),
                    supplements_pm=yn(base_compliance + 0.05),
                    # Lifestyle — cardio only 3-4x/week
                    cardio_today=yn(0.5),
                    consistent_sleep=yn(base_compliance - 0.05),
                    # Symptom scores (1-5, higher=better)
                    digestion_score=score(week_scores["digestion"]),
                    urinary_score=score(week_scores["urinary"]),
                    sinus_score=score(week_scores["sinus"]),
                    energy_score=score(week_scores["energy"]),
                    notes=None,
                )
                db.add(ci)

            await db.flush()
            print("21-day check-in history created.")
        else:
            print(f"Check-ins already exist ({len(existing_checkins)} records), skipping.")

        # ── 7. Follow-up ─────────────────────────────────────────────────────
        result = await db.execute(
            select(FollowUp).where(
                FollowUp.patient_id == patient.id,
                FollowUp.completed_at == None,
            )
        )
        existing_followup = result.scalars().first()

        if not existing_followup:
            followup_date = date.today() + timedelta(days=2)
            fu = FollowUp(
                patient_id=patient.id,
                practitioner_id=practitioner.id,
                scheduled_date=followup_date,
                reason="3-week protocol review",
                notes=(
                    "Reassess: digestion, urinary symptoms, sinus/respiratory symptoms, energy levels. "
                    "Review lab markers if new results available. "
                    "Adjust supplement timing and dosing based on response. "
                    "Consider adding Triphala if bowel regularity remains an issue."
                ),
            )
            db.add(fu)
            await db.flush()
            print(f"Scheduled follow-up: {followup_date}")
        else:
            print("Follow-up already scheduled, skipping.")

        await db.commit()
        print(f"\nDemo seed complete.")
        print(f"  Login:    {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")
        print(f"  Patient:  Shuva Mukhopadhyay (full plan + 21-day history)")


if __name__ == "__main__":
    asyncio.run(seed_demo())
