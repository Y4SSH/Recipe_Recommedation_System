from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id,
)

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    password_hash = hash_password(user.password)
    return crud.create_user(db, user, password_hash)

@router.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token, expires_in = create_access_token(db_user.id)
    return schemas.TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=db_user,
    )

@router.get("/me", response_model=schemas.User)
def me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user