from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
import json
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


@router.patch("/me", response_model=schemas.User)
def update_me(
    user_update: schemas.UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user_profile(db, user, user_update)


def _load_user_preferences(user) -> dict:
    try:
        parsed = json.loads(user.preferences or "{}")
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {}


@router.get("/pantry", response_model=schemas.PantryState)
def get_pantry(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = _load_user_preferences(user)
    items = prefs.get("pantry_items", [])
    if not isinstance(items, list):
        items = []

    sanitized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        try:
            days = int(item.get("expires_in_days", 0))
        except Exception:
            days = 0
        days = max(0, min(30, days))
        sanitized.append(schemas.PantryItem(name=name, expires_in_days=days))

    return schemas.PantryState(items=sanitized)


@router.put("/pantry", response_model=schemas.PantryState)
def update_pantry(
    pantry: schemas.PantryState,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = _load_user_preferences(user)
    dedup = []
    seen = set()
    for item in pantry.items[:100]:
        key = item.name.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        dedup.append({"name": item.name.strip(), "expires_in_days": int(item.expires_in_days)})

    prefs["pantry_items"] = dedup
    user.preferences = json.dumps(prefs)
    db.commit()
    db.refresh(user)

    return schemas.PantryState(items=[schemas.PantryItem(**item) for item in dedup])