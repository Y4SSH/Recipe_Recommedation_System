import json

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[str] = None


class PantryItem(BaseModel):
    name: str
    expires_in_days: int = Field(ge=0, le=30)


class PantryState(BaseModel):
    items: List[PantryItem]

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: str
    preferences: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

# Recipe schemas
class RecipeBase(BaseModel):
    title: str
    description: Optional[str]
    ingredients: str
    steps: str
    cuisine: Optional[str]
    tags: Optional[str]
    cook_time: int
    prep_time: int
    total_time: int
    servings: int
    difficulty: str
    nutrition: Optional[str]
    image_url: Optional[str]
    source_url: Optional[str]
    main_ingredients: Optional[str]
    # Variant tagging fields
    base_recipe: Optional[str] = None
    variant_type: Optional[str] = None
    cooking_method: Optional[str] = None
    protein_type: Optional[str] = None
    difficulty_variance: Optional[int] = None

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: str
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MyRecipeProgressUpdate(BaseModel):
    ingredients_gathered: List[int] = Field(default_factory=list)
    steps_completed: List[int] = Field(default_factory=list)
    mark_completed: bool = False


class MyRecipeOut(BaseModel):
    id: str
    user_id: str
    recipe_id: str
    status: str
    ingredients_gathered: List[int] = Field(default_factory=list)
    steps_completed: List[int] = Field(default_factory=list)
    progress_percent: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    recipe: Optional[Recipe] = None

    class Config:
        from_attributes = True

    @field_validator("ingredients_gathered", "steps_completed", mode="before")
    @classmethod
    def _parse_progress_lists(cls, value):
        if value in (None, "", []):
            return []
        if isinstance(value, list):
            parsed = value
        else:
            try:
                parsed = json.loads(value)
            except Exception:
                return []
        if not isinstance(parsed, list):
            return []
        normalized = []
        for item in parsed:
            try:
                normalized.append(int(item))
            except Exception:
                continue
        return normalized

# Recommendation schemas
class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    ingredients: Optional[List[str]] = []
    time_limit: Optional[int] = None
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    servings: Optional[int] = None
    budget_limit: Optional[float] = Field(default=None, gt=0)
    health_goal: Optional[str] = None
    waste_mode: Optional[bool] = False
    pantry_items: Optional[List[PantryItem]] = []

class Recommendation(BaseModel):
    id: str
    score: float
    reason: str
    modifications: Optional[List[str]] = []
    explanation: Optional[List[str]] = []
    missing_ingredients: Optional[List[str]] = []
    available_ingredients: Optional[List[str]] = []
    customized_instructions: Optional[str] = None
    recipe: Optional[Recipe] = None

class RecommendResponse(BaseModel):
    recommendations: List[Recommendation]


# Saved recipe schemas
class SavedRecipeActionResponse(BaseModel):
    saved: bool
    message: str
    recipe_id: str


# Rating schemas
class RatingCreate(BaseModel):
    recipe_id: str
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class RatingOut(BaseModel):
    id: str
    user_id: str
    recipe_id: str
    score: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RatingSummary(BaseModel):
    recipe_id: str
    average_score: float
    total_ratings: int
    user_rating: Optional[RatingOut] = None


class FeedbackCreate(BaseModel):
    recommended_recipe_id: str
    accepted: bool
    context: Optional[str] = None
    reason: Optional[str] = None


class FeedbackOut(BaseModel):
    id: str
    user_id: str
    context: Optional[str]
    recommended_recipe_id: str
    accepted: bool
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthDetails(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    recipes_loaded: int
    embeddings_ready: bool
    model_name: str
    users: int
    recipes: int
    ratings: int
    saved_recipes: int
    feedback_entries: int


class ModelCorpusStats(BaseModel):
    total_recipes: int
    recipes_with_image_url: int
    recipes_with_local_image: int
    unique_cuisines: int
    avg_total_time_min: float
    avg_ingredients_per_recipe: float


class ModelFeedbackStats(BaseModel):
    total_feedback: int
    accepted_feedback: int
    rejected_feedback: int
    has_feedback_signal: bool
    accuracy_proxy: float
    acceptance_rate: float
    rejection_rate: float


class ModelRatingStats(BaseModel):
    total_ratings: int
    avg_rating: float


class ModelEngineStats(BaseModel):
    model_name: str
    max_candidates: int
    embedding_cache_entries: int
    ingredient_cache_entries: int


class ModelStatsResponse(BaseModel):
    status: str
    corpus: ModelCorpusStats
    feedback: ModelFeedbackStats
    ratings: ModelRatingStats
    engine: ModelEngineStats