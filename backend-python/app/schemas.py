from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

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