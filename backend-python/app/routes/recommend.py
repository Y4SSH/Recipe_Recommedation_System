from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.recommender import recommender
from app.security import get_current_user_id

router = APIRouter()

@router.post("/", response_model=schemas.RecommendResponse)
def recommend_recipes(request: schemas.RecommendRequest, db: Session = Depends(get_db)):
    recommendations = recommender.recommend(request)
    
    # Enhance with full recipe data
    for rec in recommendations:
        if rec.recipe:
            full_recipe = crud.get_recipe(db, rec.recipe.id)
            if full_recipe:
                rec.recipe = full_recipe
    
    return schemas.RecommendResponse(recommendations=recommendations)

@router.post("/reload")
def reload_recommender(user_id: str = Depends(get_current_user_id)):
    result = recommender.reload()
    return {
        "message": "Recommender reloaded",
        "reloaded_by": user_id,
        **result,
    }