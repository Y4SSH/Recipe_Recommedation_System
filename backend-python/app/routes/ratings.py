from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=schemas.RatingOut)
def create_or_update_rating(
    rating: schemas.RatingCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, rating.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return crud.upsert_rating(db, user_id, rating)


@router.get("/me", response_model=List[schemas.RatingOut])
def get_my_ratings(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return crud.get_ratings_for_user(db, user_id)


@router.get("/recipe/{recipe_id}", response_model=schemas.RatingSummary)
def get_recipe_rating_summary(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    average_score, total_ratings = crud.get_rating_stats_for_recipe(db, recipe_id)
    user_rating = crud.get_user_rating_for_recipe(db, user_id, recipe_id)

    return schemas.RatingSummary(
        recipe_id=recipe_id,
        average_score=round(average_score, 2),
        total_ratings=total_ratings,
        user_rating=user_rating,
    )
