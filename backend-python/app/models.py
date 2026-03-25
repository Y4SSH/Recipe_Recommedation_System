from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
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

    ratings = relationship("Rating", back_populates="recipe")
    feedbacks = relationship("Feedback", back_populates="recipe")
    saved_recipes = relationship("SavedRecipe", back_populates="recipe")

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