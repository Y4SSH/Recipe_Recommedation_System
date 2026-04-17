from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    preferences = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ratings = relationship("Rating", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    saved_recipes = relationship("SavedRecipe", back_populates="user")
    my_recipes = relationship("MyRecipe", back_populates="user")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    ingredients = Column(Text)  # JSON string
    steps = Column(Text)  # JSON string
    cuisine = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string
    cook_time = Column(Integer)
    prep_time = Column(Integer)
    total_time = Column(Integer)
    servings = Column(Integer)
    difficulty = Column(String)
    nutrition = Column(Text, nullable=True)  # JSON string
    image_url = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    main_ingredients = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Variant tagging columns (added for recipe variant management)
    base_recipe = Column(String, nullable=True, index=True)  # Normalized base recipe name
    variant_type = Column(String, nullable=True, index=True)  # air_fryer, beef, slow_cooker, etc.
    cooking_method = Column(String, nullable=True)  # baked, fried, slow_cooker, etc.
    protein_type = Column(String, nullable=True)  # chicken, beef, vegetarian, etc.
    difficulty_variance = Column(Integer, nullable=True, default=50)  # 0-100 scale for similarity to base

    ratings = relationship("Rating", back_populates="recipe")
    feedbacks = relationship("Feedback", back_populates="recipe")
    saved_recipes = relationship("SavedRecipe", back_populates="recipe")
    my_recipes = relationship("MyRecipe", back_populates="recipe")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), index=True)
    score = Column(Integer)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="ratings")
    recipe = relationship("Recipe", back_populates="ratings")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    context = Column(Text)  # JSON string
    recommended_recipe_id = Column(String, ForeignKey("recipes.id"), index=True)
    accepted = Column(Boolean)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="feedbacks")
    recipe = relationship("Recipe", back_populates="feedbacks")

class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_recipes")
    recipe = relationship("Recipe", back_populates="saved_recipes")


class MyRecipe(Base):
    __tablename__ = "my_recipes"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_my_recipes_user_recipe"),
    )

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), index=True)
    status = Column(String, default="interested")
    ingredients_gathered = Column(Text, nullable=True)
    steps_completed = Column(Text, nullable=True)
    progress_percent = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="my_recipes")
    recipe = relationship("Recipe", back_populates="my_recipes")