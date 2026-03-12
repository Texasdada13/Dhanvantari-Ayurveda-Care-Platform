"""
Check-in routes — practitioner view (list a patient's check-ins).
Patient-facing check-in submission is handled in portal.py.
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_practitioner
from app.models.practitioner import Practitioner
from app.models.checkin import DailyCheckIn
from app.models.patient import Patient

router = APIRouter()


def _checkin_dict(c: DailyCheckIn) -> dict:
    return {
        "id": c.id,
        "patient_id": c.patient_id,
        "date": c.date.isoformat(),
        "submitted_at": c.submitted_at.isoformat(),
        # Morning
        "warm_water": c.warm_water,
        "breathing_exercise": c.breathing_exercise,
        "nasal_oil": c.nasal_oil,
        # Meals
        "warm_breakfast": c.warm_breakfast,
        "avoided_cold_food": c.avoided_cold_food,
        "avoided_yogurt": c.avoided_yogurt,
        "herbal_tea_am": c.herbal_tea_am,
        "warm_lunch": c.warm_lunch,
        "included_barley": c.included_barley,
        "no_cold_drinks": c.no_cold_drinks,
        "warm_dinner": c.warm_dinner,
        "dinner_before_8pm": c.dinner_before_8pm,
        # Supplements
        "supplements_am": c.supplements_am,
        "supplements_pm": c.supplements_pm,
        # Lifestyle
        "cardio_today": c.cardio_today,
        "consistent_sleep": c.consistent_sleep,
        # Scores
        "digestion_score": c.digestion_score,
        "urinary_score": c.urinary_score,
        "sinus_score": c.sinus_score,
        "energy_score": c.energy_score,
        "notes": c.notes,
        # Computed
        "habit_completion_pct": c.habit_completion_pct,
        "avg_symptom_score": c.avg_symptom_score,
    }


@router.get("/patients/{patient_id}/checkins")
async def list_checkins(
    patient_id: int,
    limit: int = Query(30, le=90),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    # Verify patient belongs to practitioner
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.practitioner_id == practitioner.id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db.execute(
        select(DailyCheckIn)
        .where(DailyCheckIn.patient_id == patient_id)
        .order_by(DailyCheckIn.date.desc())
        .limit(limit)
    )
    return [_checkin_dict(c) for c in result.scalars().all()]
