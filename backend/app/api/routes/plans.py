"""
Consultation Plan routes.
"""
from datetime import datetime, date as dateobj
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_practitioner, require_active_subscription
from app.models.practitioner import Practitioner
from app.models.plan import ConsultationPlan, PlanSupplement, PlanRecipe, Supplement, Recipe
from app.models.patient import Patient

router = APIRouter()


class PlanCreate(BaseModel):
    title: str = "Initial Protocol"
    duration_weeks: int | None = None
    start_date: str | None = None
    foods_to_avoid: str | None = None
    foods_to_include: str | None = None
    lifestyle_notes: str | None = None
    breathing_notes: str | None = None
    nasal_care_notes: str | None = None
    followup_notes: str | None = None
    ai_rationale: str | None = None


class PlanUpdate(BaseModel):
    title: str | None = None
    duration_weeks: int | None = None
    start_date: str | None = None
    active: bool | None = None
    foods_to_avoid: str | None = None
    foods_to_include: str | None = None
    lifestyle_notes: str | None = None
    breathing_notes: str | None = None
    nasal_care_notes: str | None = None
    followup_notes: str | None = None
    ai_rationale: str | None = None
    ai_generated_at: str | None = None


class AddSupplementIn(BaseModel):
    supplement_id: int
    dose: str | None = None
    timing: str | None = None
    frequency: str | None = None
    special_notes: str | None = None


class AddRecipeIn(BaseModel):
    recipe_id: int
    meal_slot: str | None = None


def _plan_dict(plan: ConsultationPlan) -> dict:
    return {
        "id": plan.id,
        "patient_id": plan.patient_id,
        "title": plan.title,
        "active": plan.active,
        "duration_weeks": plan.duration_weeks,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
        "foods_to_avoid": plan.foods_to_avoid,
        "foods_to_include": plan.foods_to_include,
        "lifestyle_notes": plan.lifestyle_notes,
        "breathing_notes": plan.breathing_notes,
        "nasal_care_notes": plan.nasal_care_notes,
        "followup_notes": plan.followup_notes,
        "ai_rationale": plan.ai_rationale,
        "ai_generated_at": plan.ai_generated_at.isoformat() if plan.ai_generated_at else None,
        "created_at": plan.created_at.isoformat(),
        "supplements": [
            {
                "id": ps.id,
                "supplement_id": ps.supplement_id,
                "name": ps.supplement.name if ps.supplement else None,
                "name_sanskrit": ps.supplement.name_sanskrit if ps.supplement else None,
                "dose": ps.dose,
                "timing": ps.timing,
                "frequency": ps.frequency,
                "special_notes": ps.special_notes,
            }
            for ps in (plan.plan_supplements or [])
        ],
        "recipes": [
            {
                "id": pr.id,
                "recipe_id": pr.recipe_id,
                "name": pr.recipe.name if pr.recipe else None,
                "meal_type": pr.recipe.meal_type if pr.recipe else None,
                "meal_slot": pr.meal_slot,
            }
            for pr in (plan.plan_recipes or [])
        ],
    }


async def _get_patient_for_practitioner(patient_id: int, practitioner: Practitioner, db: AsyncSession) -> Patient:
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.practitioner_id == practitioner.id,
            Patient.active == True,
        )
    )
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


async def _get_active_plan(patient_id: int, db: AsyncSession) -> ConsultationPlan | None:
    result = await db.execute(
        select(ConsultationPlan)
        .options(
            selectinload(ConsultationPlan.plan_supplements).selectinload(PlanSupplement.supplement),
            selectinload(ConsultationPlan.plan_recipes).selectinload(PlanRecipe.recipe),
        )
        .where(ConsultationPlan.patient_id == patient_id, ConsultationPlan.active == True)
        .order_by(ConsultationPlan.created_at.desc())
    )
    return result.scalars().first()


@router.get("/patients/{patient_id}/plan")
async def get_plan(
    patient_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    await _get_patient_for_practitioner(patient_id, practitioner, db)
    plan = await _get_active_plan(patient_id, db)
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found")
    return _plan_dict(plan)


@router.post("/patients/{patient_id}/plan", status_code=201)
async def create_plan(
    patient_id: int,
    body: PlanCreate,
    practitioner: Practitioner = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_db),
):
    await _get_patient_for_practitioner(patient_id, practitioner, db)
    result = await db.execute(
        select(ConsultationPlan).where(ConsultationPlan.patient_id == patient_id, ConsultationPlan.active == True)
    )
    for old in result.scalars().all():
        old.active = False

    start = dateobj.fromisoformat(body.start_date) if body.start_date else None
    plan = ConsultationPlan(
        patient_id=patient_id,
        title=body.title,
        duration_weeks=body.duration_weeks,
        start_date=start,
        foods_to_avoid=body.foods_to_avoid,
        foods_to_include=body.foods_to_include,
        lifestyle_notes=body.lifestyle_notes,
        breathing_notes=body.breathing_notes,
        nasal_care_notes=body.nasal_care_notes,
        followup_notes=body.followup_notes,
        ai_rationale=body.ai_rationale,
    )
    db.add(plan)
    await db.flush()
    return {"id": plan.id, "message": "Plan created"}


@router.patch("/patients/{patient_id}/plan")
async def update_plan(
    patient_id: int,
    body: PlanUpdate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    await _get_patient_for_practitioner(patient_id, practitioner, db)
    plan = await _get_active_plan(patient_id, db)
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan")
    for field, value in body.model_dump(exclude_none=True).items():
        if field == "start_date" and value:
            setattr(plan, field, dateobj.fromisoformat(value))
        elif field == "ai_generated_at" and value:
            setattr(plan, field, datetime.fromisoformat(value))
        else:
            setattr(plan, field, value)
    await db.flush()
    return {"message": "Plan updated"}


@router.post("/patients/{patient_id}/plan/supplements", status_code=201)
async def add_supplement(
    patient_id: int,
    body: AddSupplementIn,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    await _get_patient_for_practitioner(patient_id, practitioner, db)
    plan = await _get_active_plan(patient_id, db)
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan")
    result = await db.execute(select(Supplement).where(Supplement.id == body.supplement_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Supplement not found")
    ps = PlanSupplement(
        plan_id=plan.id,
        supplement_id=body.supplement_id,
        dose=body.dose,
        timing=body.timing,
        frequency=body.frequency,
        special_notes=body.special_notes,
    )
    db.add(ps)
    await db.flush()
    return {"id": ps.id, "message": "Supplement added"}


@router.delete("/plans/supplements/{ps_id}", status_code=204)
async def remove_supplement(
    ps_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PlanSupplement).where(PlanSupplement.id == ps_id))
    ps = result.scalars().first()
    if not ps:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(ps)


@router.post("/patients/{patient_id}/plan/recipes", status_code=201)
async def add_recipe(
    patient_id: int,
    body: AddRecipeIn,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    await _get_patient_for_practitioner(patient_id, practitioner, db)
    plan = await _get_active_plan(patient_id, db)
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan")
    result = await db.execute(select(Recipe).where(Recipe.id == body.recipe_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Recipe not found")
    pr = PlanRecipe(plan_id=plan.id, recipe_id=body.recipe_id, meal_slot=body.meal_slot)
    db.add(pr)
    await db.flush()
    return {"id": pr.id, "message": "Recipe added"}


@router.delete("/plans/recipes/{pr_id}", status_code=204)
async def remove_recipe(
    pr_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PlanRecipe).where(PlanRecipe.id == pr_id))
    pr = result.scalars().first()
    if not pr:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(pr)
