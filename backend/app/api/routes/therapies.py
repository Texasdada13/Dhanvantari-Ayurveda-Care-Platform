"""
Therapy services library, service packages, and plan assignment routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_practitioner
from app.models.practitioner import Practitioner
from app.models.therapy import Therapy, ServicePackage, PackageTherapy, PlanTherapy, PlanServicePackage

router = APIRouter()
package_router = APIRouter()
plan_therapy_router = APIRouter()
plan_package_router = APIRouter()


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class TherapyCreate(BaseModel):
    name: str
    name_sanskrit: str | None = None
    description: str | None = None
    category: str | None = None
    default_duration_minutes: int | None = None
    default_price_cents: int | None = None
    benefits: list[str] | None = None
    contraindications: list[str] | None = None
    dosha_effect: str | None = None
    image_url: str | None = None


class TherapyUpdate(BaseModel):
    name: str | None = None
    name_sanskrit: str | None = None
    description: str | None = None
    category: str | None = None
    default_duration_minutes: int | None = None
    default_price_cents: int | None = None
    benefits: list[str] | None = None
    contraindications: list[str] | None = None
    dosha_effect: str | None = None
    image_url: str | None = None


class PackageCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    total_duration_minutes: int | None = None
    total_price_cents: int | None = None
    includes_extras: list[str] | None = None
    panchakarma_days: int | None = None
    therapy_ids: list[int] | None = None


class PackageUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    total_duration_minutes: int | None = None
    total_price_cents: int | None = None
    includes_extras: list[str] | None = None
    panchakarma_days: int | None = None


class PlanTherapyCreate(BaseModel):
    therapy_id: int
    frequency: str | None = None
    duration_minutes: int | None = None
    price_cents: int | None = None
    notes: str | None = None
    scheduled_date: str | None = None


class PlanTherapyUpdate(BaseModel):
    frequency: str | None = None
    duration_minutes: int | None = None
    price_cents: int | None = None
    notes: str | None = None
    scheduled_date: str | None = None


class PlanPackageCreate(BaseModel):
    package_id: int
    price_cents: int | None = None
    start_date: str | None = None
    notes: str | None = None


class ReorderBody(BaseModel):
    ids: list[int]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _therapy_dict(t: Therapy) -> dict:
    return {
        "id": t.id,
        "practitioner_id": t.practitioner_id,
        "name": t.name,
        "name_sanskrit": t.name_sanskrit,
        "description": t.description,
        "category": t.category,
        "default_duration_minutes": t.default_duration_minutes,
        "default_price_cents": t.default_price_cents,
        "benefits": t.benefits or [],
        "contraindications": t.contraindications or [],
        "dosha_effect": t.dosha_effect,
        "image_url": t.image_url,
        "is_community": t.is_community,
        "is_active": t.is_active,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _package_dict(p: ServicePackage, include_therapies: bool = False) -> dict:
    d = {
        "id": p.id,
        "practitioner_id": p.practitioner_id,
        "name": p.name,
        "description": p.description,
        "category": p.category,
        "total_duration_minutes": p.total_duration_minutes,
        "total_price_cents": p.total_price_cents,
        "includes_extras": p.includes_extras or [],
        "panchakarma_days": p.panchakarma_days,
        "image_url": p.image_url,
        "is_community": p.is_community,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
    if include_therapies and p.package_therapies:
        d["therapies"] = [
            {
                "id": pt.id,
                "therapy_id": pt.therapy_id,
                "therapy": _therapy_dict(pt.therapy) if pt.therapy else None,
                "sort_order": pt.sort_order,
                "override_duration_minutes": pt.override_duration_minutes,
                "notes": pt.notes,
            }
            for pt in sorted(p.package_therapies, key=lambda x: x.sort_order)
        ]
    return d


# ── Therapy CRUD ─────────────────────────────────────────────────────────────

@router.get("")
async def list_therapies(
    search: str | None = Query(None),
    category: str | None = Query(None),
    dosha: str | None = Query(None),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    q = select(Therapy).where(Therapy.is_active == True)
    if search:
        q = q.where(
            or_(
                Therapy.name.ilike(f"%{search}%"),
                Therapy.name_sanskrit.ilike(f"%{search}%"),
                Therapy.description.ilike(f"%{search}%"),
            )
        )
    if category:
        q = q.where(Therapy.category.ilike(f"%{category}%"))
    if dosha:
        q = q.where(Therapy.dosha_effect.ilike(f"%{dosha}%"))
    q = q.order_by(Therapy.name)
    result = await db.execute(q)
    return [_therapy_dict(t) for t in result.scalars().all()]


@router.post("", status_code=201)
async def create_therapy(
    body: TherapyCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    t = Therapy(practitioner_id=practitioner.id, is_community=False, **body.model_dump())
    db.add(t)
    await db.flush()
    return {"id": t.id, "message": "Therapy created"}


@router.get("/{therapy_id}")
async def get_therapy(
    therapy_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Therapy).where(Therapy.id == therapy_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Therapy not found")
    return _therapy_dict(t)


@router.patch("/{therapy_id}")
async def update_therapy(
    therapy_id: int,
    body: TherapyUpdate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Therapy).where(Therapy.id == therapy_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Therapy not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(t, field, value)
    await db.flush()
    return {"message": "Updated"}


@router.delete("/{therapy_id}", status_code=204)
async def delete_therapy(
    therapy_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Therapy).where(Therapy.id == therapy_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Therapy not found")
    t.is_active = False
    await db.flush()
    return None


# ── Package CRUD ─────────────────────────────────────────────────────────────

@package_router.get("")
async def list_packages(
    search: str | None = Query(None),
    category: str | None = Query(None),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    q = select(ServicePackage).where(ServicePackage.is_active == True).options(
        selectinload(ServicePackage.package_therapies).selectinload(PackageTherapy.therapy)
    )
    if search:
        q = q.where(
            or_(
                ServicePackage.name.ilike(f"%{search}%"),
                ServicePackage.description.ilike(f"%{search}%"),
            )
        )
    if category:
        q = q.where(ServicePackage.category.ilike(f"%{category}%"))
    q = q.order_by(ServicePackage.name)
    result = await db.execute(q)
    return [_package_dict(p, include_therapies=True) for p in result.scalars().unique().all()]


@package_router.post("", status_code=201)
async def create_package(
    body: PackageCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude={"therapy_ids"})
    pkg = ServicePackage(practitioner_id=practitioner.id, is_community=False, **data)
    db.add(pkg)
    await db.flush()
    if body.therapy_ids:
        for idx, tid in enumerate(body.therapy_ids):
            db.add(PackageTherapy(package_id=pkg.id, therapy_id=tid, sort_order=idx))
        await db.flush()
    return {"id": pkg.id, "message": "Package created"}


@package_router.get("/{package_id}")
async def get_package(
    package_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ServicePackage).where(ServicePackage.id == package_id).options(
            selectinload(ServicePackage.package_therapies).selectinload(PackageTherapy.therapy)
        )
    )
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Package not found")
    return _package_dict(p, include_therapies=True)


@package_router.patch("/{package_id}")
async def update_package(
    package_id: int,
    body: PackageUpdate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ServicePackage).where(ServicePackage.id == package_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Package not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    await db.flush()
    return {"message": "Updated"}


@package_router.delete("/{package_id}", status_code=204)
async def delete_package(
    package_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ServicePackage).where(ServicePackage.id == package_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Package not found")
    p.is_active = False
    await db.flush()
    return None


@package_router.post("/{package_id}/therapies", status_code=201)
async def add_therapy_to_package(
    package_id: int,
    therapy_id: int = Query(...),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    pt = PackageTherapy(package_id=package_id, therapy_id=therapy_id)
    db.add(pt)
    await db.flush()
    return {"id": pt.id, "message": "Therapy added to package"}


@package_router.delete("/{package_id}/therapies/{pt_id}", status_code=204)
async def remove_therapy_from_package(
    package_id: int,
    pt_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PackageTherapy).where(PackageTherapy.id == pt_id, PackageTherapy.package_id == package_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
    return None


# ── Plan Therapy Assignment ──────────────────────────────────────────────────

@plan_therapy_router.get("/{plan_id}/therapies")
async def list_plan_therapies(
    plan_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanTherapy).where(PlanTherapy.plan_id == plan_id).order_by(PlanTherapy.sort_order, PlanTherapy.id)
    )
    items = result.scalars().all()
    out = []
    for item in items:
        tresult = await db.execute(select(Therapy).where(Therapy.id == item.therapy_id))
        therapy = tresult.scalars().first()
        out.append({
            "id": item.id,
            "plan_id": item.plan_id,
            "therapy_id": item.therapy_id,
            "frequency": item.frequency,
            "duration_minutes": item.duration_minutes,
            "price_cents": item.price_cents,
            "notes": item.notes,
            "sort_order": item.sort_order,
            "scheduled_date": item.scheduled_date.isoformat() if item.scheduled_date else None,
            "therapy": _therapy_dict(therapy) if therapy else None,
        })
    return out


@plan_therapy_router.post("/{plan_id}/therapies", status_code=201)
async def assign_therapy_to_plan(
    plan_id: int,
    body: PlanTherapyCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    tresult = await db.execute(select(Therapy).where(Therapy.id == body.therapy_id))
    if not tresult.scalars().first():
        raise HTTPException(status_code=404, detail="Therapy not found")
    data = body.model_dump()
    item = PlanTherapy(plan_id=plan_id, **data)
    db.add(item)
    await db.flush()
    return {"id": item.id, "message": "Therapy assigned to plan"}


@plan_therapy_router.patch("/{plan_id}/therapies/{assignment_id}")
async def update_plan_therapy(
    plan_id: int,
    assignment_id: int,
    body: PlanTherapyUpdate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanTherapy).where(PlanTherapy.id == assignment_id, PlanTherapy.plan_id == plan_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Assignment not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    await db.flush()
    return {"message": "Updated"}


@plan_therapy_router.delete("/{plan_id}/therapies/{assignment_id}", status_code=204)
async def remove_therapy_from_plan(
    plan_id: int,
    assignment_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanTherapy).where(PlanTherapy.id == assignment_id, PlanTherapy.plan_id == plan_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await db.delete(item)
    return None


@plan_therapy_router.put("/{plan_id}/therapies/reorder")
async def reorder_plan_therapies(
    plan_id: int,
    body: ReorderBody,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    for idx, assignment_id in enumerate(body.ids):
        result = await db.execute(
            select(PlanTherapy).where(PlanTherapy.id == assignment_id, PlanTherapy.plan_id == plan_id)
        )
        item = result.scalars().first()
        if item:
            item.sort_order = idx
    await db.flush()
    return {"message": "Reordered"}


# ── Plan Package Assignment ──────────────────────────────────────────────────

@plan_package_router.get("/{plan_id}/packages")
async def list_plan_packages(
    plan_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanServicePackage).where(PlanServicePackage.plan_id == plan_id).order_by(PlanServicePackage.sort_order, PlanServicePackage.id)
    )
    items = result.scalars().all()
    out = []
    for item in items:
        presult = await db.execute(
            select(ServicePackage).where(ServicePackage.id == item.package_id).options(
                selectinload(ServicePackage.package_therapies).selectinload(PackageTherapy.therapy)
            )
        )
        pkg = presult.scalars().first()
        out.append({
            "id": item.id,
            "plan_id": item.plan_id,
            "package_id": item.package_id,
            "price_cents": item.price_cents,
            "start_date": item.start_date.isoformat() if item.start_date else None,
            "notes": item.notes,
            "sort_order": item.sort_order,
            "package": _package_dict(pkg, include_therapies=True) if pkg else None,
        })
    return out


@plan_package_router.post("/{plan_id}/packages", status_code=201)
async def assign_package_to_plan(
    plan_id: int,
    body: PlanPackageCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    presult = await db.execute(select(ServicePackage).where(ServicePackage.id == body.package_id))
    if not presult.scalars().first():
        raise HTTPException(status_code=404, detail="Package not found")
    item = PlanServicePackage(plan_id=plan_id, **body.model_dump())
    db.add(item)
    await db.flush()
    return {"id": item.id, "message": "Package assigned to plan"}


@plan_package_router.delete("/{plan_id}/packages/{assignment_id}", status_code=204)
async def remove_package_from_plan(
    plan_id: int,
    assignment_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanServicePackage).where(PlanServicePackage.id == assignment_id, PlanServicePackage.plan_id == plan_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await db.delete(item)
    return None
