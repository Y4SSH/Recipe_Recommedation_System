from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import get_current_user_id

router = APIRouter()


@router.get("/", response_model=List[schemas.MyRecipeOut])
def get_my_recipes(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return crud.get_my_recipes_for_user(db, user_id)


@router.post("/{recipe_id}/interested", response_model=schemas.MyRecipeOut)
def mark_interested(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return crud.upsert_my_recipe_interest(db, user_id, recipe_id)


@router.post("/{recipe_id}/start", response_model=schemas.MyRecipeOut)
def start_recipe(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    active = crud.get_active_my_recipe_for_user(db, user_id)
    if active and active.recipe_id != recipe_id:
        raise HTTPException(status_code=409, detail="Finish your active recipe before starting another one")

    return crud.start_my_recipe(db, user_id, recipe_id)


@router.patch("/{recipe_id}/progress", response_model=schemas.MyRecipeOut)
def update_progress(
    recipe_id: str,
    payload: schemas.MyRecipeProgressUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    active = crud.get_active_my_recipe_for_user(db, user_id)
    if active and active.recipe_id != recipe_id:
        raise HTTPException(status_code=409, detail="Finish your active recipe before updating another one")

    return crud.update_my_recipe_progress(
        db,
        user_id,
        recipe_id,
        payload.ingredients_gathered,
        payload.steps_completed,
        mark_completed=payload.mark_completed,
    )


@router.post("/{recipe_id}/complete", response_model=schemas.MyRecipeOut)
def complete_recipe(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    active = crud.get_active_my_recipe_for_user(db, user_id)
    if active and active.recipe_id != recipe_id:
        raise HTTPException(status_code=409, detail="Finish your active recipe before completing another one")

    return crud.complete_my_recipe(db, user_id, recipe_id)