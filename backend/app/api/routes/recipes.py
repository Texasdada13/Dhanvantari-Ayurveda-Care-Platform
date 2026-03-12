"""
Recipes library routes.
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


class RecipeUpdate(BaseModel):
    name: str | None = None
    meal_type: str | None = None
    dosha_good_for: str | None = None
    dosha_avoid: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    notes: str | None = None
    is_tea: bool | None = None


def _recipe_dict(r: Recipe) -> dict:
    return {
        "id": r.id,
        "name": r.name,
        "meal_type": r.meal_type,
        "dosha_good_for": r.dosha_good_for,
        "dosha_avoid": r.dosha_avoid,
        "ingredients": r.ingredients,
        "instructions": r.instructions,
        "notes": r.notes,
        "is_tea": r.is_tea,
        "is_community": r.is_community,
    }


@router.get("")
async def list_recipes(
    search: str | None = Query(None),
    meal_type: str | None = Query(None),
    dosha: str | None = Query(None),
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    q = select(Recipe)
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
    r = Recipe(**body.model_dump())
    db.add(r)
    await db.flush()
    return {"id": r.id, "message": "Recipe created"}


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
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(r, field, value)
    await db.flush()
    return {"message": "Updated"}
