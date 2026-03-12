"""
Patient portal routes — token-only authentication, no login required.
All routes are /api/portal/{token}/*
"""
from datetime import datetime, date, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.models.checkin import CheckInToken, DailyCheckIn
from app.models.patient import Patient
from app.models.plan import ConsultationPlan, PlanSupplement, PlanRecipe
from app.models.followup import FollowUp

router = APIRouter()


# ── Token resolution helper ───────────────────────────────────────────────────

async def _resolve_token(token: str, db: AsyncSession) -> tuple[CheckInToken, Patient]:
    result = await db.execute(
        select(CheckInToken)
        .options(selectinload(CheckInToken.patient))
        .where(CheckInToken.token == token, CheckInToken.active == True)
    )
    tok = result.scalars().first()
    if not tok or not tok.patient or not tok.patient.active:
        raise HTTPException(status_code=404, detail="Invalid or expired portal link")
    return tok, tok.patient


# ── Check-in schema ───────────────────────────────────────────────────────────

class CheckInSubmit(BaseModel):
    warm_water: bool = False
    breathing_exercise: bool = False
    nasal_oil: bool = False
    warm_breakfast: bool = False
    avoided_cold_food: bool = False
    avoided_yogurt: bool = False
    herbal_tea_am: bool = False
    warm_lunch: bool = False
    included_barley: bool = False
    no_cold_drinks: bool = False
    warm_dinner: bool = False
    dinner_before_8pm: bool = False
    supplements_am: bool = False
    supplements_pm: bool = False
    cardio_today: bool = False
    consistent_sleep: bool = False
    digestion_score: int | None = None
    urinary_score: int | None = None
    sinus_score: int | None = None
    energy_score: int | None = None
    notes: str | None = None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/{token}")
async def portal_home(token: str, db: AsyncSession = Depends(get_db)):
    tok, patient = await _resolve_token(token, db)
    today = date.today()

    # Active plan
    plan_result = await db.execute(
        select(ConsultationPlan)
        .options(
            selectinload(ConsultationPlan.plan_supplements).selectinload(PlanSupplement.supplement),
            selectinload(ConsultationPlan.plan_recipes).selectinload(PlanRecipe.recipe),
        )
        .where(ConsultationPlan.patient_id == patient.id, ConsultationPlan.active == True)
        .order_by(ConsultationPlan.created_at.desc())
    )
    plan = plan_result.scalars().first()

    # Today's check-in
    today_ci_result = await db.execute(
        select(DailyCheckIn).where(DailyCheckIn.patient_id == patient.id, DailyCheckIn.date == today)
    )
    today_checkin = today_ci_result.scalars().first()

    # Streak calculation
    all_checkins_result = await db.execute(
        select(DailyCheckIn.date)
        .where(DailyCheckIn.patient_id == patient.id)
        .order_by(DailyCheckIn.date.desc())
        .limit(60)
    )
    checkin_dates = set(row[0] for row in all_checkins_result.all())
    streak = 0
    check_date = today if today in checkin_dates else (today.replace(day=today.day - 1) if today.day > 1 else today)
    from datetime import timedelta
    current = today
    while current in checkin_dates:
        streak += 1
        current = current - timedelta(days=1)

    # Next follow-up
    fu_result = await db.execute(
        select(FollowUp)
        .where(
            FollowUp.patient_id == patient.id,
            FollowUp.completed == False,
            FollowUp.scheduled_date >= today,
        )
        .order_by(FollowUp.scheduled_date)
        .limit(1)
    )
    next_followup = fu_result.scalars().first()

    # Days since first check-in
    first_ci_result = await db.execute(
        select(func.min(DailyCheckIn.date)).where(DailyCheckIn.patient_id == patient.id)
    )
    first_date = first_ci_result.scalar()
    days_since_start = (today - first_date).days if first_date else 0

    return {
        "patient": {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
        },
        "today_checkin_done": today_checkin is not None,
        "streak": streak,
        "days_since_start": days_since_start,
        "plan_summary": {
            "id": plan.id,
            "title": plan.title,
            "supplement_count": len(plan.plan_supplements),
            "recipe_count": len(plan.plan_recipes),
        } if plan else None,
        "next_followup": {
            "id": next_followup.id,
            "scheduled_date": next_followup.scheduled_date.isoformat(),
            "reason": next_followup.reason,
            "days_until": (next_followup.scheduled_date - today).days,
        } if next_followup else None,
    }


@router.get("/{token}/plan")
async def portal_plan(token: str, db: AsyncSession = Depends(get_db)):
    tok, patient = await _resolve_token(token, db)

    plan_result = await db.execute(
        select(ConsultationPlan)
        .options(
            selectinload(ConsultationPlan.plan_supplements).selectinload(PlanSupplement.supplement),
            selectinload(ConsultationPlan.plan_recipes).selectinload(PlanRecipe.recipe),
        )
        .where(ConsultationPlan.patient_id == patient.id, ConsultationPlan.active == True)
        .order_by(ConsultationPlan.created_at.desc())
    )
    plan = plan_result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan")

    return {
        "id": plan.id,
        "title": plan.title,
        "duration_weeks": plan.duration_weeks,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "foods_to_avoid": plan.foods_to_avoid,
        "foods_to_include": plan.foods_to_include,
        "lifestyle_notes": plan.lifestyle_notes,
        "breathing_notes": plan.breathing_notes,
        "nasal_care_notes": plan.nasal_care_notes,
        "supplements": [
            {
                "name": ps.supplement.name,
                "name_sanskrit": ps.supplement.name_sanskrit,
                "dose": ps.dose,
                "timing": ps.timing,
                "frequency": ps.frequency,
                "purpose": ps.supplement.purpose,
                "special_notes": ps.special_notes,
            }
            for ps in plan.plan_supplements if ps.supplement
        ],
        "recipes": [
            {
                "name": pr.recipe.name,
                "meal_type": pr.recipe.meal_type,
                "meal_slot": pr.meal_slot,
                "ingredients": pr.recipe.ingredients,
                "instructions": pr.recipe.instructions,
                "notes": pr.recipe.notes,
            }
            for pr in plan.plan_recipes if pr.recipe
        ],
    }


@router.get("/{token}/history")
async def portal_history(token: str, db: AsyncSession = Depends(get_db)):
    tok, patient = await _resolve_token(token, db)

    result = await db.execute(
        select(DailyCheckIn)
        .where(DailyCheckIn.patient_id == patient.id)
        .order_by(DailyCheckIn.date.desc())
        .limit(90)
    )
    checkins = result.scalars().all()

    return {
        "checkins": [
            {
                "date": c.date.isoformat(),
                "habit_completion_pct": c.habit_completion_pct,
                "digestion_score": c.digestion_score,
                "urinary_score": c.urinary_score,
                "sinus_score": c.sinus_score,
                "energy_score": c.energy_score,
                "avg_symptom_score": c.avg_symptom_score,
                "notes": c.notes,
            }
            for c in checkins
        ]
    }


@router.post("/{token}/checkin", status_code=201)
async def portal_checkin(token: str, body: CheckInSubmit, db: AsyncSession = Depends(get_db)):
    tok, patient = await _resolve_token(token, db)
    today = date.today()

    # Prevent duplicate check-in
    existing = await db.execute(
        select(DailyCheckIn).where(DailyCheckIn.patient_id == patient.id, DailyCheckIn.date == today)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Already checked in today")

    ci = DailyCheckIn(patient_id=patient.id, date=today, **body.model_dump())
    db.add(ci)
    await db.flush()
    return {"message": "Check-in saved", "habit_completion_pct": ci.habit_completion_pct}


@router.get("/{token}/followups")
async def portal_followups(token: str, db: AsyncSession = Depends(get_db)):
    tok, patient = await _resolve_token(token, db)
    today = date.today()

    result = await db.execute(
        select(FollowUp)
        .where(FollowUp.patient_id == patient.id)
        .order_by(FollowUp.scheduled_date)
    )
    followups = result.scalars().all()

    upcoming = []
    past = []
    for fu in followups:
        d = {
            "id": fu.id,
            "scheduled_date": fu.scheduled_date.isoformat(),
            "reason": fu.reason,
            "notes": fu.notes,
            "completed": fu.completed,
            "completed_at": fu.completed_at.isoformat() if fu.completed_at else None,
        }
        if fu.completed or fu.scheduled_date < today:
            past.append(d)
        else:
            d["days_until"] = (fu.scheduled_date - today).days
            upcoming.append(d)

    return {"upcoming": upcoming, "past": past}
