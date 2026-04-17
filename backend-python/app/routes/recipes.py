from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db
from app.image_utils import resolve_recipe_image_url

router = APIRouter()

@router.get("/", response_model=List[schemas.Recipe])
def get_recipes(skip: int = 0, limit: int = 100, search: Optional[str] = None, cuisine: Optional[str] = None, diet: Optional[str] = None, image_only: Optional[bool] = False, include_duplicates: Optional[bool] = False, db: Session = Depends(get_db)):
    recipes = crud.get_recipes(
        db,
        skip=skip,
        limit=limit,
        search=search,
        cuisine=cuisine,
        diet=diet,
        image_only=image_only,
        dedupe_titles=not bool(include_duplicates),
    )
    for recipe in recipes:
        recipe.image_url = resolve_recipe_image_url(recipe.title, recipe.image_url)
    return recipes

@router.get("/{recipe_id}", response_model=schemas.Recipe)
def get_recipe(recipe_id: str, db: Session = Depends(get_db)):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.image_url = resolve_recipe_image_url(recipe.title, recipe.image_url)
    return recipe