from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
import json
import uuid

def get_recipes(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Recipe)
    if search:
        search_term = f"%{search}%"
        query = query.filter(models.Recipe.title.ilike(search_term) | models.Recipe.cuisine.ilike(search_term))
    return query.offset(skip).limit(limit).all()

def get_all_recipes(db: Session):
    return db.query(models.Recipe).all()

def get_recipe(db: Session, recipe_id: str):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def create_recipe(db: Session, recipe: schemas.RecipeCreate):
    db_recipe = models.Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate, password_hash: str):
    db_user = models.User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        password_hash=password_hash,
        preferences=None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_profile(db: Session, user: models.User, user_update: schemas.UserUpdate):
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.preferences is not None:
        user.preferences = user_update.preferences

    db.commit()
    db.refresh(user)
    return user


def get_saved_recipe(db: Session, user_id: str, recipe_id: str):
    return (
        db.query(models.SavedRecipe)
        .filter(models.SavedRecipe.user_id == user_id, models.SavedRecipe.recipe_id == recipe_id)
        .first()
    )


def get_saved_recipes_for_user(db: Session, user_id: str):
    return (
        db.query(models.Recipe)
        .join(models.SavedRecipe, models.SavedRecipe.recipe_id == models.Recipe.id)
        .filter(models.SavedRecipe.user_id == user_id)
        .order_by(models.SavedRecipe.created_at.desc())
        .all()
    )


def add_saved_recipe(db: Session, user_id: str, recipe_id: str):
    saved = models.SavedRecipe(
        id=str(uuid.uuid4()),
        user_id=user_id,
        recipe_id=recipe_id,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


def remove_saved_recipe(db: Session, user_id: str, recipe_id: str) -> bool:
    saved = get_saved_recipe(db, user_id, recipe_id)
    if not saved:
        return False

    db.delete(saved)
    db.commit()
    return True


def get_user_rating_for_recipe(db: Session, user_id: str, recipe_id: str):
    return (
        db.query(models.Rating)
        .filter(models.Rating.user_id == user_id, models.Rating.recipe_id == recipe_id)
        .first()
    )


def upsert_rating(db: Session, user_id: str, rating: schemas.RatingCreate):
    existing = get_user_rating_for_recipe(db, user_id, rating.recipe_id)
    if existing:
        existing.score = rating.score
        existing.comment = rating.comment
        db.commit()
        db.refresh(existing)
        return existing

    new_rating = models.Rating(
        id=str(uuid.uuid4()),
        user_id=user_id,
        recipe_id=rating.recipe_id,
        score=rating.score,
        comment=rating.comment,
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


def get_ratings_for_user(db: Session, user_id: str):
    return (
        db.query(models.Rating)
        .filter(models.Rating.user_id == user_id)
        .order_by(models.Rating.created_at.desc())
        .all()
    )


def get_rating_stats_for_recipe(db: Session, recipe_id: str):
    avg_score, total_ratings = (
        db.query(func.avg(models.Rating.score), func.count(models.Rating.id))
        .filter(models.Rating.recipe_id == recipe_id)
        .one()
    )
    return float(avg_score or 0.0), int(total_ratings or 0)


def create_feedback(db: Session, user_id: str, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(
        id=str(uuid.uuid4()),
        user_id=user_id,
        context=feedback.context,
        recommended_recipe_id=feedback.recommended_recipe_id,
        accepted=feedback.accepted,
        reason=feedback.reason,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_feedback_for_user(db: Session, user_id: str):
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.user_id == user_id)
        .order_by(models.Feedback.created_at.desc())
        .all()
    )


def get_health_counts(db: Session):
    return {
        "users": db.query(func.count(models.User.id)).scalar() or 0,
        "recipes": db.query(func.count(models.Recipe.id)).scalar() or 0,
        "ratings": db.query(func.count(models.Rating.id)).scalar() or 0,
        "saved_recipes": db.query(func.count(models.SavedRecipe.id)).scalar() or 0,
        "feedback_entries": db.query(func.count(models.Feedback.id)).scalar() or 0,
    }