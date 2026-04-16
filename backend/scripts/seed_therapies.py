"""
Seed AyurRoots therapy services and packages.

Run from backend/: python scripts/seed_therapies.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import Base
from app.models.therapy import Therapy, ServicePackage, PackageTherapy

_db_url = settings.DATABASE_URL
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_db_url)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ── Individual Therapies ─────────────────────────────────────────────────────

THERAPIES = [
    {
        "name": "Abhyanga",
        "name_sanskrit": "Abhyanga (अभ्यङ्ग)",
        "category": "Massage",
        "description": "Traditional Ayurvedic full-body warm oil massage that stimulates the skin, circulation, muscles, joints, and deeper structures. Promotes relaxation and nourishment of tissues.",
        "default_duration_minutes": 60,
        "default_price_cents": 12500,
        "benefits": ["Improves circulation", "Nourishes tissues", "Reduces Vata", "Promotes deep relaxation", "Supports lymphatic drainage"],
        "contraindications": ["Fever", "Acute inflammation", "Skin infections", "During menstruation"],
        "dosha_effect": "Reduces Vata, calms Pitta",
    },
    {
        "name": "Shirodhara",
        "name_sanskrit": "Shirodhara (शिरोधारा)",
        "category": "Head Therapy",
        "description": "Warm herbal oils are gently streamed over the third eye and forehead, inducing a deep state of mental relaxation and clarity.",
        "default_duration_minutes": 60,
        "default_price_cents": 12500,
        "benefits": ["Deep mental relaxation", "Reduces anxiety and stress", "Improves sleep quality", "Balances nervous system", "Enhances mental clarity"],
        "contraindications": ["Brain tumor", "Recent neck injury", "Acute fever"],
        "dosha_effect": "Calms Vata and Pitta",
    },
    {
        "name": "Shirodhara with Marma Points",
        "name_sanskrit": "Shirodhara Marma (शिरोधारा मर्म)",
        "category": "Head Therapy",
        "description": "Extended Shirodhara session with additional head marma points massage for deeper therapeutic effect.",
        "default_duration_minutes": 60,
        "default_price_cents": 16500,
        "benefits": ["Deep mental relaxation", "Opens energy channels", "Relieves headaches", "Balances nervous system"],
        "contraindications": ["Brain tumor", "Recent neck injury"],
        "dosha_effect": "Calms Vata and Pitta",
    },
    {
        "name": "Marma Points Massage",
        "name_sanskrit": "Marma Chikitsa (मर्म चिकित्सा)",
        "category": "Massage",
        "description": "Therapeutic massage targeting the 107 vital energy points (marma) to open energy channels and bring calm and rejuvenation.",
        "default_duration_minutes": 60,
        "default_price_cents": 16500,
        "benefits": ["Opens energy channels", "Relieves chronic pain", "Balances prana flow", "Enhances immunity", "Promotes rejuvenation"],
        "contraindications": ["Open wounds at marma sites", "Acute inflammation"],
        "dosha_effect": "Balances all three doshas",
    },
    {
        "name": "Swedana",
        "name_sanskrit": "Swedana (स्वेदन)",
        "category": "Steam",
        "description": "Herbal steam therapy that opens the channels (srotas), promotes sweating, and helps eliminate toxins. Typically follows Abhyanga.",
        "default_duration_minutes": 20,
        "default_price_cents": 5000,
        "benefits": ["Opens body channels", "Promotes sweating", "Eliminates toxins", "Relieves stiffness", "Improves circulation"],
        "contraindications": ["Pregnancy", "Heart disease", "Extreme debility", "Bleeding disorders"],
        "dosha_effect": "Reduces Vata and Kapha",
    },
    {
        "name": "Nasyam",
        "name_sanskrit": "Nasya (नस्य)",
        "category": "Detox",
        "description": "Nasal passage clearing therapy including facial massage with herbal steam, followed by medicated oil administration into nasal passages.",
        "default_duration_minutes": 30,
        "default_price_cents": 7500,
        "benefits": ["Clears sinuses", "Improves breathing", "Relieves headaches", "Enhances mental clarity", "Nourishes brain tissue"],
        "contraindications": ["Acute cold with heavy congestion", "Nasal polyps", "Just after eating"],
        "dosha_effect": "Reduces Kapha, calms Vata in head region",
    },
    {
        "name": "Kati Basti",
        "name_sanskrit": "Kati Basti (कटि बस्ति)",
        "category": "Basti",
        "description": "Warm medicated oil held over the lower back using a dough dam. Deeply nourishing therapy for lumbar spine and lower back pain.",
        "default_duration_minutes": 45,
        "default_price_cents": 12500,
        "benefits": ["Relieves lower back pain", "Nourishes lumbar spine", "Reduces sciatica symptoms", "Strengthens back muscles"],
        "contraindications": ["Skin lesions in area", "Acute spinal injury"],
        "dosha_effect": "Reduces Vata in lower back",
    },
    {
        "name": "Greeva Basti",
        "name_sanskrit": "Greeva Basti (ग्रीवा बस्ति)",
        "category": "Basti",
        "description": "Warm medicated oil held over the neck and cervical spine area. Therapeutic for neck pain, cervical spondylosis, and stiffness.",
        "default_duration_minutes": 45,
        "default_price_cents": 12500,
        "benefits": ["Relieves neck pain", "Reduces cervical stiffness", "Nourishes cervical spine", "Relieves shoulder tension"],
        "contraindications": ["Skin lesions in area", "Acute cervical injury"],
        "dosha_effect": "Reduces Vata in neck region",
    },
    {
        "name": "Janu Basti",
        "name_sanskrit": "Janu Basti (जानु बस्ति)",
        "category": "Basti",
        "description": "Warm medicated oil held over the knee joint. Highly effective for knee pain, osteoarthritis, and joint stiffness.",
        "default_duration_minutes": 45,
        "default_price_cents": 12500,
        "benefits": ["Relieves knee pain", "Reduces joint inflammation", "Nourishes cartilage", "Improves mobility"],
        "contraindications": ["Skin infection on knee", "Open wounds"],
        "dosha_effect": "Reduces Vata in joints",
    },
    {
        "name": "Netra Tarpana",
        "name_sanskrit": "Netra Tarpana (नेत्र तर्पण)",
        "category": "Basti",
        "description": "Warm medicated ghee held over the eyes using a dough dam. Deeply nourishing for eye strain, dry eyes, and vision support.",
        "default_duration_minutes": 60,
        "default_price_cents": 17500,
        "benefits": ["Relieves eye strain", "Nourishes eye tissues", "Improves vision clarity", "Reduces dry eyes", "Soothes Pitta in eyes"],
        "contraindications": ["Eye infection", "Conjunctivitis", "Glaucoma"],
        "dosha_effect": "Reduces Pitta and Vata in eyes",
    },
    {
        "name": "Pinda Swedana",
        "name_sanskrit": "Pinda Sweda (पिण्ड स्वेद)",
        "category": "Massage",
        "description": "Therapeutic massage using warm rice boluses (Navarakizhi). Provides strength and nutrition to body tissues, especially bones and muscles.",
        "default_duration_minutes": 60,
        "default_price_cents": 18500,
        "benefits": ["Strengthens muscles and bones", "Nourishes tissues", "Relieves joint pain", "Promotes tissue regeneration", "Improves skin texture"],
        "contraindications": ["Fever", "Acute inflammation", "Diabetes (uncontrolled)"],
        "dosha_effect": "Reduces Vata, nourishes all tissues",
    },
    {
        "name": "Patra Pinda Swedana",
        "name_sanskrit": "Patra Pinda Sweda (पत्र पिण्ड स्वेद)",
        "category": "Massage",
        "description": "Pain-relieving therapy using herbal leaf boluses with dry herbs. Effective for chronic pain, inflammation, and stiffness.",
        "default_duration_minutes": 60,
        "default_price_cents": 18500,
        "benefits": ["Relieves chronic pain", "Reduces inflammation", "Improves joint mobility", "Reduces swelling", "Promotes circulation"],
        "contraindications": ["Fever", "Skin infections", "Open wounds"],
        "dosha_effect": "Reduces Vata and Kapha",
    },
    {
        "name": "Udvartana",
        "name_sanskrit": "Udvartana (उद्वर्तन)",
        "category": "Exfoliating",
        "description": "Herbal body scrub with massage that exfoliates skin, firms tissues, and helps with weight management and cellulite.",
        "default_duration_minutes": 60,
        "default_price_cents": 18500,
        "benefits": ["Exfoliates skin", "Firms tissues", "Supports weight management", "Improves skin texture", "Reduces cellulite"],
        "contraindications": ["Skin sensitivity", "Open wounds", "Very dry skin"],
        "dosha_effect": "Reduces Kapha, stimulates metabolism",
    },
    {
        "name": "Mukha Lepam",
        "name_sanskrit": "Mukha Lepa (मुख लेप)",
        "category": "Facial",
        "description": "Anti-aging Ayurvedic facial massage with herbal paste application. Rejuvenates facial skin, reduces fine lines, and promotes a natural glow.",
        "default_duration_minutes": 60,
        "default_price_cents": 14500,
        "benefits": ["Anti-aging", "Reduces fine lines", "Promotes natural glow", "Nourishes facial skin", "Improves complexion"],
        "contraindications": ["Active acne infection", "Skin allergy to herbs"],
        "dosha_effect": "Balances Pitta, nourishes skin",
    },
    {
        "name": "Pure & Natural Facial",
        "name_sanskrit": None,
        "category": "Facial",
        "description": "Natural facial massage using pure Ayurvedic oils and herbal preparations. Cleansing, toning, and moisturizing for all skin types.",
        "default_duration_minutes": 45,
        "default_price_cents": 12500,
        "benefits": ["Deep cleansing", "Toning", "Moisturizing", "Promotes relaxation", "Improves skin health"],
        "contraindications": ["Active skin infection"],
        "dosha_effect": "Balances all doshas",
    },
    {
        "name": "Indian Head Massage",
        "name_sanskrit": "Shiro Abhyanga (शिरो अभ्यङ्ग)",
        "category": "Head Therapy",
        "description": "Traditional Indian head massage with marma point stimulation. Relieves headaches, tension, and promotes mental clarity.",
        "default_duration_minutes": 30,
        "default_price_cents": 7500,
        "benefits": ["Relieves headaches", "Reduces tension", "Promotes mental clarity", "Improves sleep", "Nourishes hair and scalp"],
        "contraindications": ["Head injury", "Scalp infection"],
        "dosha_effect": "Calms Vata and Pitta",
    },
    {
        "name": "Prenatal Massage",
        "name_sanskrit": "Garbhini Abhyanga (गर्भिणी अभ्यङ्ग)",
        "category": "Prenatal",
        "description": "Gentle Ayurvedic massage specifically designed for expectant mothers. Promotes relaxation, reduces pregnancy discomfort, and supports maternal wellness.",
        "default_duration_minutes": 60,
        "default_price_cents": 15000,
        "benefits": ["Reduces pregnancy discomfort", "Promotes relaxation", "Improves sleep", "Reduces swelling", "Supports maternal wellness"],
        "contraindications": ["High-risk pregnancy", "First trimester (consult doctor)"],
        "dosha_effect": "Calms Vata, nurtures mother and baby",
    },
    {
        "name": "Postpartum Massage",
        "name_sanskrit": "Sutika Abhyanga (सूतिका अभ्यङ्ग)",
        "category": "Prenatal",
        "description": "Specialized Ayurvedic massage for new mothers. Supports postpartum recovery, helps restore strength, and promotes healing. 40-day packages available.",
        "default_duration_minutes": 60,
        "default_price_cents": 16500,
        "benefits": ["Supports postpartum recovery", "Restores strength", "Promotes healing", "Reduces stress", "Supports lactation"],
        "contraindications": ["Cesarean section (wait for healing)", "Postpartum complications"],
        "dosha_effect": "Reduces Vata, restores balance",
    },
    {
        "name": "Rose Massage & Steam",
        "name_sanskrit": None,
        "category": "Massage",
        "description": "Luxurious massage using rose-infused oils followed by herbal steam. A pampering experience that nourishes skin and uplifts mood.",
        "default_duration_minutes": 60,
        "default_price_cents": 18500,
        "benefits": ["Nourishes skin", "Uplifts mood", "Promotes relaxation", "Balances emotions", "Aromatic therapy"],
        "contraindications": ["Rose allergy", "Skin sensitivity"],
        "dosha_effect": "Calms Pitta, balances emotions",
    },
]

# ── Combination Packages ─────────────────────────────────────────────────────

PACKAGES = [
    {
        "name": "Shirodhara + Abhyanga",
        "category": "Combination",
        "description": "Our most popular combination — warm oil full-body massage followed by the deeply calming Shirodhara head oil treatment.",
        "total_duration_minutes": 90,
        "total_price_cents": 18500,
        "therapy_names": ["Shirodhara", "Abhyanga"],
    },
    {
        "name": "Shirodhara + Indian Head Marma",
        "category": "Combination",
        "description": "Third eye oil therapy combined with Indian head massage and marma point stimulation for total head and mind relaxation.",
        "total_duration_minutes": 60,
        "total_price_cents": 16500,
        "therapy_names": ["Shirodhara", "Indian Head Massage"],
    },
    {
        "name": "Abhyanga + Herbal Bolus",
        "category": "Combination",
        "description": "Full-body warm oil massage combined with herbal leaf bolus therapy for deep pain relief and tissue nourishment.",
        "total_duration_minutes": 60,
        "total_price_cents": 18500,
        "therapy_names": ["Abhyanga", "Patra Pinda Swedana"],
    },
    {
        "name": "Herbal Scrub + Abhyanga",
        "category": "Combination",
        "description": "Exfoliating herbal scrub followed by warm oil massage. Detoxifying, skin-firming, and deeply relaxing.",
        "total_duration_minutes": 60,
        "total_price_cents": 18500,
        "therapy_names": ["Udvartana", "Abhyanga"],
    },
    {
        "name": "Abhyanga + Herbal Steam",
        "category": "Combination",
        "description": "Classic Ayurvedic purification combination — warm oil massage followed by herbal steam to open channels and eliminate toxins.",
        "total_duration_minutes": 75,
        "total_price_cents": 16500,
        "therapy_names": ["Abhyanga", "Swedana"],
    },
]

# ── Pampering Packages ───────────────────────────────────────────────────────

PAMPERING = [
    {
        "name": "Full Day Pampering Experience (Utsav)",
        "category": "Pampering",
        "description": "A luxurious 4-hour Ayurvedic spa day featuring consultation, foot bath, Abhyanga, Shirodhara, body scrub, facial, steam, and complimentary lunch and herbal tea.",
        "total_duration_minutes": 240,
        "total_price_cents": 49900,
        "includes_extras": ["Consultation", "Foot bath", "Body scrub", "Facial", "Steam", "Lunch", "Herbal tea"],
        "therapy_names": ["Abhyanga", "Shirodhara"],
    },
    {
        "name": "Half Day Pampering (Utsav)",
        "category": "Pampering",
        "description": "A rejuvenating 2.5-hour Ayurvedic spa experience with foot massage, body and facial massage, and your choice of Shirodhara or Udvartana scrub.",
        "total_duration_minutes": 150,
        "total_price_cents": 32500,
        "includes_extras": ["Foot massage", "Choice of Shirodhara or Udvartana"],
        "therapy_names": ["Abhyanga", "Mukha Lepam"],
    },
]

# ── Panchakarma Programs ─────────────────────────────────────────────────────

PANCHAKARMA = [
    {
        "name": "Panchakarma — 1 Day Detox",
        "category": "Panchakarma",
        "description": "A concentrated single-day Ayurvedic detox experience customized by Vaidya Meenakshi Gupta. Includes consultation, Nadi Pariksha (pulse diagnosis), customized body therapies, and an individualized diet plan.",
        "total_duration_minutes": 180,
        "total_price_cents": 29900,
        "panchakarma_days": 1,
        "includes_extras": ["Consultation", "Nadi Pariksha (pulse diagnosis)", "Customized body therapies", "Individualized diet plan", "2 complimentary sinus & ear therapies"],
    },
    {
        "name": "Panchakarma — 3 Day Detox",
        "category": "Panchakarma",
        "description": "Three-day intensive Ayurvedic detoxification and rejuvenation program. Each day features personalized body therapies, dietary guidance, and practitioner supervision.",
        "total_duration_minutes": 540,
        "total_price_cents": 79900,
        "panchakarma_days": 3,
        "includes_extras": ["Consultation", "Nadi Pariksha (pulse diagnosis)", "Customized daily body therapies", "Individualized diet plan", "2 complimentary sinus & ear therapies"],
    },
    {
        "name": "Panchakarma — 5 Day Detox",
        "category": "Panchakarma",
        "description": "Five-day comprehensive Panchakarma purification program. The full detox cycle with progressive daily therapies tailored to your constitution and imbalances.",
        "total_duration_minutes": 900,
        "total_price_cents": 124900,
        "panchakarma_days": 5,
        "includes_extras": ["Consultation", "Nadi Pariksha (pulse diagnosis)", "Customized daily body therapies", "Individualized diet plan", "2 complimentary sinus & ear therapies"],
    },
    {
        "name": "Panchakarma — 7 Day Detox",
        "category": "Panchakarma",
        "description": "Seven-day deep Panchakarma rejuvenation — the gold standard Ayurvedic detoxification program. Reduces inflammation, builds immunity, reverses stress effects, and supports total body-mind cleansing.",
        "total_duration_minutes": 1260,
        "total_price_cents": 169900,
        "panchakarma_days": 7,
        "includes_extras": ["Consultation", "Nadi Pariksha (pulse diagnosis)", "Customized daily body therapies", "Individualized diet plan", "2 complimentary sinus & ear therapies"],
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as db:
        # Check if already seeded
        result = await db.execute(select(Therapy).limit(1))
        if result.scalars().first():
            print("Therapies already seeded, skipping.")
            return

        # Seed individual therapies
        therapy_map = {}
        for t_data in THERAPIES:
            t = Therapy(**t_data, is_community=True)
            db.add(t)
            await db.flush()
            therapy_map[t.name] = t.id
            print(f"  + Therapy: {t.name} (${t.default_price_cents / 100:.0f}/{t.default_duration_minutes}min)")

        # Seed combination packages
        for p_data in PACKAGES:
            therapy_names = p_data.pop("therapy_names", [])
            pkg = ServicePackage(**p_data, is_community=True)
            db.add(pkg)
            await db.flush()
            for idx, name in enumerate(therapy_names):
                if name in therapy_map:
                    db.add(PackageTherapy(package_id=pkg.id, therapy_id=therapy_map[name], sort_order=idx))
            print(f"  + Package: {pkg.name} (${pkg.total_price_cents / 100:.0f})")

        # Seed pampering packages
        for p_data in PAMPERING:
            therapy_names = p_data.pop("therapy_names", [])
            pkg = ServicePackage(**p_data, is_community=True)
            db.add(pkg)
            await db.flush()
            for idx, name in enumerate(therapy_names):
                if name in therapy_map:
                    db.add(PackageTherapy(package_id=pkg.id, therapy_id=therapy_map[name], sort_order=idx))
            print(f"  + Pampering: {pkg.name} (${pkg.total_price_cents / 100:.0f})")

        # Seed Panchakarma programs
        for p_data in PANCHAKARMA:
            pkg = ServicePackage(**p_data, is_community=True)
            db.add(pkg)
            await db.flush()
            print(f"  + Panchakarma: {pkg.name} ({pkg.panchakarma_days}-day)")

        await db.commit()
        print(f"\nSeeded {len(THERAPIES)} therapies + {len(PACKAGES) + len(PAMPERING) + len(PANCHAKARMA)} packages")


if __name__ == "__main__":
    asyncio.run(seed())
