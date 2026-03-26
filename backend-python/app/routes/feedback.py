from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=schemas.FeedbackOut)
def submit_feedback(
    feedback: schemas.FeedbackCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, feedback.recommended_recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return crud.create_feedback(db, user_id, feedback)


@router.get("/me", response_model=List[schemas.FeedbackOut])
def get_my_feedback(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return crud.get_feedback_for_user(db, user_id)
