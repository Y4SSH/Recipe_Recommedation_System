from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import get_current_user_id

router = APIRouter()


@router.get("/", response_model=List[schemas.Recipe])
def get_my_saved_recipes(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return crud.get_saved_recipes_for_user(db, user_id)


@router.post("/{recipe_id}", response_model=schemas.SavedRecipeActionResponse)
def save_recipe(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    existing = crud.get_saved_recipe(db, user_id, recipe_id)
    if existing:
        return schemas.SavedRecipeActionResponse(
            saved=True,
            message="Recipe already saved",
            recipe_id=recipe_id,
        )

    crud.add_saved_recipe(db, user_id, recipe_id)
    return schemas.SavedRecipeActionResponse(
        saved=True,
        message="Recipe saved",
        recipe_id=recipe_id,
    )


@router.delete("/{recipe_id}", response_model=schemas.SavedRecipeActionResponse)
def unsave_recipe(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    removed = crud.remove_saved_recipe(db, user_id, recipe_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Saved recipe not found")

    return schemas.SavedRecipeActionResponse(
        saved=False,
        message="Recipe removed from saved list",
        recipe_id=recipe_id,
    )
