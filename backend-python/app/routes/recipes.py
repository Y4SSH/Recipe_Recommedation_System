from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Recipe])
def get_recipes(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
    recipes = crud.get_recipes(db, skip=skip, limit=limit, search=search)
    return recipes

@router.get("/{recipe_id}", response_model=schemas.Recipe)
def get_recipe(recipe_id: str, db: Session = Depends(get_db)):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe