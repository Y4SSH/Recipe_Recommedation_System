from sqlalchemy.orm import Session
from app import models, schemas
import json
import uuid

def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Recipe).offset(skip).limit(limit).all()

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