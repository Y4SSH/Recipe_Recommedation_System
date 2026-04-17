from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy import case


def _parse_int_list(value):
    if value in (None, ""):
        return []
    if isinstance(value, list):
        items = value
    else:
        try:
            items = json.loads(value)
        except Exception:
            items = []
    normalized = []
    for item in items:
        try:
            normalized.append(int(item))
        except Exception:
            continue
    return sorted(set(normalized))


def _parse_recipe_items(recipe: models.Recipe, field_name: str) -> list:
    raw_value = getattr(recipe, field_name, None)
    if not raw_value:
        return []
    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        return []
    return []


def _compute_my_recipe_progress(recipe: models.Recipe, ingredients_gathered: list, steps_completed: list) -> int:
    total_ingredients = len(_parse_recipe_items(recipe, "ingredients"))
    total_steps = len(_parse_recipe_items(recipe, "steps"))

    progress_parts = []
    if total_ingredients > 0:
        progress_parts.append(min(1.0, len(_parse_int_list(ingredients_gathered)) / float(total_ingredients)))
    if total_steps > 0:
        progress_parts.append(min(1.0, len(_parse_int_list(steps_completed)) / float(total_steps)))

    if not progress_parts:
        return 0

    return int(round((sum(progress_parts) / len(progress_parts)) * 100))

def get_recipes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    cuisine: str = None,
    diet: str = None,
    image_only: bool = False,
    dedupe_titles: bool = True,
):
    query = db.query(models.Recipe)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(models.Recipe.title.ilike(search_term) | models.Recipe.main_ingredients.ilike(search_term))
        
    if cuisine:
        cuisine_term = f"%{cuisine}%"
        query = query.filter(models.Recipe.cuisine.ilike(cuisine_term))
        
    if diet:
        if diet == "veg":
            # The tags are dumped JSON arrays like '["indian", "veg"]'
            query = query.filter(models.Recipe.tags.ilike('%"veg"%'))
        elif diet == "non-veg":
            query = query.filter(models.Recipe.tags.ilike('%"non-veg"%'))

    if image_only:
        from sqlalchemy import or_
        IMAGE_TITLES = [
            "Aloo Gobi", "Butter Chicken", "Chana Masala", "Chicken Biryani", 
            "Dal Tadka", "Dosa", "Gulab Jamun", "Hydrebadi Biryani", "Kheer", 
            "Litti Choka", "Malai Kofta", "Palak Paneer", "Pani Puri", "Pav Bhaji", 
            "Prawn Curry", "Rajma", "Rogan Josh", "Samosa", "Vegetable Korma", "Vindaloo"
        ]
        filters = [models.Recipe.title.ilike(f"%{t}%") for t in IMAGE_TITLES]
        query = query.filter(or_(*filters))

    ordered_query = query.order_by(models.Recipe.title.asc(), models.Recipe.id.asc())

    if not dedupe_titles:
        return ordered_query.offset(skip).limit(limit).all()

    # Fast dedupe path: scan in batches and collapse by base_recipe/title in Python.
    # This avoids expensive SQL GROUP BY subqueries on large datasets.
    target_count = max(0, skip) + max(0, limit)
    if target_count == 0:
        return []

    chunk_size = max(200, limit * 10)
    offset = 0
    max_scan = 20000
    scanned = 0

    order = []
    grouped = {}

    while len(order) < target_count and scanned < max_scan:
        batch = ordered_query.offset(offset).limit(chunk_size).all()
        if not batch:
            break

        for recipe in batch:
            key = (recipe.base_recipe or recipe.title or "").strip().lower()
            if not key:
                key = str(recipe.id)

            existing = grouped.get(key)
            if existing is None:
                grouped[key] = recipe
                order.append(key)
            else:
                existing_is_standard = (existing.variant_type or "").strip().lower() == "standard"
                recipe_is_standard = (recipe.variant_type or "").strip().lower() == "standard"
                if recipe_is_standard and not existing_is_standard:
                    grouped[key] = recipe

        offset += chunk_size
        scanned += len(batch)

    unique_recipes = [grouped[k] for k in order]
    return unique_recipes[skip: skip + limit]

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


def get_user_preferences_json(user: models.User) -> dict:
    try:
        parsed = json.loads(user.preferences or "{}")
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {}


def set_user_preferences_json(db: Session, user: models.User, preferences: dict):
    user.preferences = json.dumps(preferences)
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


def update_learning_profile_from_feedback(db: Session, user_id: str, recipe: models.Recipe, accepted: bool):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    preferences = get_user_preferences_json(user)
    learning = preferences.get("learning_profile", {})
    if not isinstance(learning, dict):
        learning = {}

    accepted_cuisines = learning.get("accepted_cuisines", {})
    rejected_cuisines = learning.get("rejected_cuisines", {})
    accepted_tags = learning.get("accepted_tags", {})
    rejected_tags = learning.get("rejected_tags", {})
    if not isinstance(accepted_cuisines, dict):
        accepted_cuisines = {}
    if not isinstance(rejected_cuisines, dict):
        rejected_cuisines = {}
    if not isinstance(accepted_tags, dict):
        accepted_tags = {}
    if not isinstance(rejected_tags, dict):
        rejected_tags = {}

    cuisine = (recipe.cuisine or "").strip().lower()
    tags = []
    try:
        parsed_tags = json.loads(recipe.tags or "[]")
        if isinstance(parsed_tags, list):
            tags = [str(tag).strip().lower() for tag in parsed_tags if str(tag).strip()]
    except Exception:
        tags = []

    learning["feedback_count"] = int(learning.get("feedback_count", 0) or 0) + 1
    if accepted:
        learning["accepted_count"] = int(learning.get("accepted_count", 0) or 0) + 1
        if cuisine:
            accepted_cuisines[cuisine] = int(accepted_cuisines.get(cuisine, 0) or 0) + 1
        for tag in tags:
            accepted_tags[tag] = int(accepted_tags.get(tag, 0) or 0) + 1
    else:
        learning["rejected_count"] = int(learning.get("rejected_count", 0) or 0) + 1
        if cuisine:
            rejected_cuisines[cuisine] = int(rejected_cuisines.get(cuisine, 0) or 0) + 1
        for tag in tags:
            rejected_tags[tag] = int(rejected_tags.get(tag, 0) or 0) + 1

    learning["accepted_cuisines"] = accepted_cuisines
    learning["rejected_cuisines"] = rejected_cuisines
    learning["accepted_tags"] = accepted_tags
    learning["rejected_tags"] = rejected_tags
    preferences["learning_profile"] = learning

    return set_user_preferences_json(db, user, preferences)


def get_user_learning_profile(db: Session, user_id: str) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        return {}
    preferences = get_user_preferences_json(user)
    learning = preferences.get("learning_profile", {})
    return learning if isinstance(learning, dict) else {}


def get_feedback_for_user(db: Session, user_id: str):
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.user_id == user_id)
        .order_by(models.Feedback.created_at.desc())
        .all()
    )


def get_my_recipe(db: Session, user_id: str, recipe_id: str):
    return (
        db.query(models.MyRecipe)
        .options(joinedload(models.MyRecipe.recipe))
        .filter(models.MyRecipe.user_id == user_id, models.MyRecipe.recipe_id == recipe_id)
        .first()
    )


def get_active_my_recipe_for_user(db: Session, user_id: str):
    return (
        db.query(models.MyRecipe)
        .options(joinedload(models.MyRecipe.recipe))
        .filter(models.MyRecipe.user_id == user_id, models.MyRecipe.status == "in_progress")
        .order_by(models.MyRecipe.updated_at.desc().nullslast())
        .first()
    )


def get_my_recipes_for_user(db: Session, user_id: str):
    status_rank = case(
        (models.MyRecipe.status == "in_progress", 0),
        (models.MyRecipe.status == "interested", 1),
        (models.MyRecipe.status == "completed", 2),
        else_=3,
    )
    return (
        db.query(models.MyRecipe)
        .options(joinedload(models.MyRecipe.recipe))
        .filter(models.MyRecipe.user_id == user_id)
        .order_by(status_rank, models.MyRecipe.updated_at.desc().nullslast(), models.MyRecipe.created_at.desc())
        .all()
    )


def upsert_my_recipe_interest(db: Session, user_id: str, recipe_id: str):
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return None

    record = get_my_recipe(db, user_id, recipe_id)
    if record:
        if record.status not in {"in_progress", "completed"}:
            record.status = "interested"
            if not record.ingredients_gathered:
                record.ingredients_gathered = json.dumps([])
            if not record.steps_completed:
                record.steps_completed = json.dumps([])
            record.progress_percent = _compute_my_recipe_progress(recipe, record.ingredients_gathered, record.steps_completed)
            db.commit()
            db.refresh(record)
    else:
        record = models.MyRecipe(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipe_id=recipe_id,
            status="interested",
            ingredients_gathered=json.dumps([]),
            steps_completed=json.dumps([]),
            progress_percent=0,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

    return get_my_recipe(db, user_id, recipe_id)


def start_my_recipe(db: Session, user_id: str, recipe_id: str):
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return None

    record = get_my_recipe(db, user_id, recipe_id)
    if not record:
        record = models.MyRecipe(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipe_id=recipe_id,
            status="in_progress",
            ingredients_gathered=json.dumps([]),
            steps_completed=json.dumps([]),
            progress_percent=0,
            started_at=datetime.now(timezone.utc),
        )
        db.add(record)
    else:
        if record.status != "in_progress":
            record.ingredients_gathered = json.dumps([])
            record.steps_completed = json.dumps([])
            record.progress_percent = 0
            record.completed_at = None
        record.status = "in_progress"
        record.started_at = record.started_at or datetime.now(timezone.utc)

    db.commit()
    db.refresh(record)
    return get_my_recipe(db, user_id, recipe_id)


def update_my_recipe_progress(db: Session, user_id: str, recipe_id: str, ingredients_gathered: list, steps_completed: list, mark_completed: bool = False):
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return None

    record = get_my_recipe(db, user_id, recipe_id)
    if not record:
        record = models.MyRecipe(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipe_id=recipe_id,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
        )
        db.add(record)

    gathered = _parse_int_list(ingredients_gathered)
    completed = _parse_int_list(steps_completed)
    record.ingredients_gathered = json.dumps(gathered)
    record.steps_completed = json.dumps(completed)
    record.progress_percent = _compute_my_recipe_progress(recipe, gathered, completed)

    if mark_completed:
        record.status = "completed"
        record.completed_at = datetime.now(timezone.utc)
        record.progress_percent = 100
    elif record.status == "completed":
        record.status = "in_progress"
        record.completed_at = None

    db.commit()
    db.refresh(record)
    return get_my_recipe(db, user_id, recipe_id)


def complete_my_recipe(db: Session, user_id: str, recipe_id: str):
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return None

    record = get_my_recipe(db, user_id, recipe_id)
    if not record:
        record = models.MyRecipe(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipe_id=recipe_id,
            status="completed",
            ingredients_gathered=json.dumps([]),
            steps_completed=json.dumps([]),
            progress_percent=100,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(record)
    else:
        record.status = "completed"
        record.progress_percent = 100
        record.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(record)
    return get_my_recipe(db, user_id, recipe_id)


def get_health_counts(db: Session):
    return {
        "users": db.query(func.count(models.User.id)).scalar() or 0,
        "recipes": db.query(func.count(models.Recipe.id)).scalar() or 0,
        "ratings": db.query(func.count(models.Rating.id)).scalar() or 0,
        "saved_recipes": db.query(func.count(models.SavedRecipe.id)).scalar() or 0,
        "feedback_entries": db.query(func.count(models.Feedback.id)).scalar() or 0,
    }


def get_model_statistics(db: Session):
    total_recipes = db.query(func.count(models.Recipe.id)).scalar() or 0
    recipes_with_image_url = (
        db.query(func.count(models.Recipe.id))
        .filter(models.Recipe.image_url.isnot(None), models.Recipe.image_url != "")
        .scalar()
        or 0
    )
    recipes_with_local_image = (
        db.query(func.count(models.Recipe.id))
        .filter(models.Recipe.image_url.like("/static/recipes/%"))
        .scalar()
        or 0
    )
    unique_cuisines = db.query(func.count(func.distinct(models.Recipe.cuisine))).scalar() or 0
    avg_total_time = db.query(func.avg(models.Recipe.total_time)).scalar() or 0.0

    recipes = db.query(models.Recipe.main_ingredients).all()
    total_ingredient_entries = 0
    valid_recipe_rows = 0
    for row in recipes:
        parsed = []
        try:
            parsed = json.loads(row[0] or "[]")
            if not isinstance(parsed, list):
                parsed = []
        except Exception:
            parsed = []
        total_ingredient_entries += len(parsed)
        valid_recipe_rows += 1

    avg_ingredients_per_recipe = (
        float(total_ingredient_entries) / float(valid_recipe_rows) if valid_recipe_rows > 0 else 0.0
    )

    total_feedback = db.query(func.count(models.Feedback.id)).scalar() or 0
    accepted_feedback = (
        db.query(func.count(models.Feedback.id)).filter(models.Feedback.accepted.is_(True)).scalar() or 0
    )
    rejected_feedback = (
        db.query(func.count(models.Feedback.id)).filter(models.Feedback.accepted.is_(False)).scalar() or 0
    )

    acceptance_rate = (float(accepted_feedback) / float(total_feedback)) if total_feedback > 0 else 0.0
    rejection_rate = (float(rejected_feedback) / float(total_feedback)) if total_feedback > 0 else 0.0
    has_feedback_signal = total_feedback > 0
    accuracy_proxy = acceptance_rate

    total_ratings = db.query(func.count(models.Rating.id)).scalar() or 0
    avg_rating = db.query(func.avg(models.Rating.score)).scalar() or 0.0

    return {
        "corpus": {
            "total_recipes": int(total_recipes),
            "recipes_with_image_url": int(recipes_with_image_url),
            "recipes_with_local_image": int(recipes_with_local_image),
            "unique_cuisines": int(unique_cuisines),
            "avg_total_time_min": round(float(avg_total_time), 2),
            "avg_ingredients_per_recipe": round(float(avg_ingredients_per_recipe), 2),
        },
        "feedback": {
            "total_feedback": int(total_feedback),
            "accepted_feedback": int(accepted_feedback),
            "rejected_feedback": int(rejected_feedback),
            "has_feedback_signal": bool(has_feedback_signal),
            "accuracy_proxy": round(accuracy_proxy, 4),
            "acceptance_rate": round(acceptance_rate, 4),
            "rejection_rate": round(rejection_rate, 4),
        },
        "ratings": {
            "total_ratings": int(total_ratings),
            "avg_rating": round(float(avg_rating), 2),
        },
    }