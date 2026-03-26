from pydantic import BaseModel, Field
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

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: str
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Recommendation schemas
class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    ingredients: Optional[List[str]] = []
    time_limit: Optional[int] = None
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    servings: Optional[int] = None

class Recommendation(BaseModel):
    id: str
    score: float
    reason: str
    modifications: Optional[List[str]] = []
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
    status: str
    recipes_loaded: int
    embeddings_ready: bool
    model_name: str
    users: int
    recipes: int
    ratings: int
    saved_recipes: int
    feedback_entries: int