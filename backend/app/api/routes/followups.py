"""
Follow-up routes — schedule, list, and complete follow-ups.
"""
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_practitioner
from app.models.practitioner import Practitioner
from app.models.followup import FollowUp
from app.models.patient import Patient

router = APIRouter()


class FollowUpCreate(BaseModel):
    patient_id: int
    scheduled_date: str
    reason: str | None = None
    notes: str | None = None


class FollowUpUpdate(BaseModel):
    scheduled_date: str | None = None
    reason: str | None = None
    notes: str | None = None
    completed: bool | None = None


def _fu_dict(fu: FollowUp) -> dict:
    return {
        "id": fu.id,
        "patient_id": fu.patient_id,
        "practitioner_id": fu.practitioner_id,
        "scheduled_date": fu.scheduled_date.isoformat(),
        "reason": fu.reason,
        "notes": fu.notes,
        "completed": fu.completed,
        "completed_at": fu.completed_at.isoformat() if fu.completed_at else None,
        "created_at": fu.created_at.isoformat(),
    }


@router.get("")
async def list_followups(
    completed: bool | None = Query(None),
    patient_id: int | None = Query(None),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    q = select(FollowUp).where(FollowUp.practitioner_id == practitioner.id)
    if completed is not None:
        q = q.where(FollowUp.completed == completed)
    if patient_id:
        q = q.where(FollowUp.patient_id == patient_id)
    q = q.order_by(FollowUp.scheduled_date)
    result = await db.execute(q)
    return [_fu_dict(fu) for fu in result.scalars().all()]


@router.post("", status_code=201)
async def create_followup(
    body: FollowUpCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    # Verify patient belongs to practitioner
    result = await db.execute(
        select(Patient).where(Patient.id == body.patient_id, Patient.practitioner_id == practitioner.id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Patient not found")

    fu = FollowUp(
        patient_id=body.patient_id,
        practitioner_id=practitioner.id,
        scheduled_date=date.fromisoformat(body.scheduled_date),
        reason=body.reason,
        notes=body.notes,
    )
    db.add(fu)
    await db.flush()
    return {"id": fu.id, "message": "Follow-up scheduled"}


@router.patch("/{followup_id}")
async def update_followup(
    followup_id: int,
    body: FollowUpUpdate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FollowUp).where(FollowUp.id == followup_id, FollowUp.practitioner_id == practitioner.id)
    )
    fu = result.scalars().first()
    if not fu:
        raise HTTPException(status_code=404, detail="Not found")

    if body.scheduled_date:
        fu.scheduled_date = date.fromisoformat(body.scheduled_date)
    if body.reason is not None:
        fu.reason = body.reason
    if body.notes is not None:
        fu.notes = body.notes
    if body.completed is not None:
        fu.completed = body.completed
        if body.completed and not fu.completed_at:
            fu.completed_at = datetime.now(timezone.utc)

    await db.flush()
    return _fu_dict(fu)


@router.delete("/{followup_id}", status_code=204)
async def delete_followup(
    followup_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FollowUp).where(FollowUp.id == followup_id, FollowUp.practitioner_id == practitioner.id)
    )
    fu = result.scalars().first()
    if not fu:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(fu)
