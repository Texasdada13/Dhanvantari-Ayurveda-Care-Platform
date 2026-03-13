"""
Recipes library routes with practitioner ownership.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_practitioner
from app.models.practitioner import Practitioner
from app.models.plan import Recipe

router = APIRouter()


class RecipeCreate(BaseModel):
    name: str
    meal_type: str | None = None
    dosha_good_for: str | None = None
    dosha_avoid: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    notes: str | None = None
    is_tea: bool = False
    category: str | None = None
    rasa: str | None = None
    virya: str | None = None
    vipaka: str | None = None
    visibility: str = "practice"


class RecipeUpdate(BaseModel):
    name: str | None = None
    meal_type: str | None = None
    dosha_good_for: str | None = None
    dosha_avoid: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    notes: str | None = None
    is_tea: bool | None = None
    category: str | None = None
    rasa: str | None = None
    virya: str | None = None
    vipaka: str | None = None
    visibility: str | None = None


def _recipe_dict(r: Recipe) -> dict:
    return {
        "id": r.id,
        "practitioner_id": r.practitioner_id,
        "name": r.name,
        "meal_type": r.meal_type,
        "dosha_good_for": r.dosha_good_for,
        "dosha_avoid": r.dosha_avoid,
        "ingredients": r.ingredients,
        "instructions": r.instructions,
        "notes": r.notes,
        "is_tea": r.is_tea,
        "is_community": r.is_community,
        "visibility": r.visibility or "community",
        "category": r.category,
        "rasa": r.rasa,
        "virya": r.virya,
        "vipaka": r.vipaka,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("")
async def list_recipes(
    search: str | None = Query(None),
    meal_type: str | None = Query(None),
    dosha: str | None = Query(None),
    mine: bool | None = Query(None),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    q = select(Recipe)

    # Filter: community recipes + practitioner's own recipes
    if mine:
        q = q.where(Recipe.practitioner_id == practitioner.id)
    else:
        q = q.where(
            or_(Recipe.practitioner_id.is_(None), Recipe.practitioner_id == practitioner.id)
        )

    if search:
        q = q.where(or_(Recipe.name.ilike(f"%{search}%"), Recipe.notes.ilike(f"%{search}%")))
    if meal_type:
        q = q.where(Recipe.meal_type.ilike(f"%{meal_type}%"))
    if dosha:
        q = q.where(Recipe.dosha_good_for.ilike(f"%{dosha}%"))
    q = q.order_by(Recipe.name)
    result = await db.execute(q)
    return [_recipe_dict(r) for r in result.scalars().all()]


@router.post("", status_code=201)
async def create_recipe(
    body: RecipeCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    r = Recipe(
        practitioner_id=practitioner.id,
        **body.model_dump(),
    )
    db.add(r)
    await db.flush()
    return _recipe_dict(r)


@router.get("/{recipe_id}")
async def get_recipe(
    recipe_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return _recipe_dict(r)


@router.patch("/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    body: RecipeUpdate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id)
    )
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    # Only the owner or community recipes can be edited
    if r.practitioner_id and r.practitioner_id != practitioner.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this recipe")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(r, field, value)
    await db.flush()
    return _recipe_dict(r)


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(
    recipe_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.practitioner_id == practitioner.id)
    )
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found or not yours to delete")
    await db.delete(r)
