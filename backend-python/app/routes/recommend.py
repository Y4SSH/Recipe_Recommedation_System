from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.image_utils import resolve_recipe_image_url
from app.security import get_current_user_id

router = APIRouter()

_recommender_instance = None


def get_recommender_instance():
    global _recommender_instance
    if _recommender_instance is not None:
        return _recommender_instance

    try:
        from app.recommender import recommender as loaded_recommender
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Recommendation engine unavailable: {exc}",
        )

    _recommender_instance = loaded_recommender
    return _recommender_instance

@router.post("/", response_model=schemas.RecommendResponse)
def recommend_recipes(request: schemas.RecommendRequest, db: Session = Depends(get_db)):
    recommender = get_recommender_instance()
    recommendations = recommender.recommend(request)

    # Resolve local image URLs without extra DB round-trips.
    for rec in recommendations:
        if rec.recipe:
            rec.recipe.image_url = resolve_recipe_image_url(rec.recipe.title, rec.recipe.image_url)

    return schemas.RecommendResponse(recommendations=recommendations)

@router.post("/reload")
def reload_recommender(user_id: str = Depends(get_current_user_id)):
    recommender = get_recommender_instance()
    result = recommender.reload()
    return {
        "message": "Recommender reloaded",
        "reloaded_by": user_id,
        **result,
    }


@router.get("/stats", response_model=schemas.ModelStatsResponse)
def get_recommender_stats(db: Session = Depends(get_db)):
    recommender = get_recommender_instance()
    db_stats = crud.get_model_statistics(db)

    return schemas.ModelStatsResponse(
        status="ok",
        corpus=schemas.ModelCorpusStats(**db_stats["corpus"]),
        feedback=schemas.ModelFeedbackStats(**db_stats["feedback"]),
        ratings=schemas.ModelRatingStats(**db_stats["ratings"]),
        engine=schemas.ModelEngineStats(
            model_name="all-MiniLM-L6-v2",
            max_candidates=getattr(recommender, "max_candidates", 0),
            embedding_cache_entries=len(getattr(recommender, "embedding_cache", {})),
            ingredient_cache_entries=len(getattr(recommender, "ingredient_pair_cache", {})),
        ),
    )