from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.recommender import recommender
from app.routes import auth, recipes, recommend, saved, ratings, feedback
import uvicorn

app = FastAPI(title="Recipe Recommender API", version="1.0.0")

import os

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
app.include_router(saved.router, prefix="/saved", tags=["saved"])
app.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])

@app.get("/")
def read_root():
    return {"message": "Recipe Recommender API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/details", response_model=schemas.HealthDetails)
def health_details(db: Session = Depends(get_db)):
    counts = crud.get_health_counts(db)
    return schemas.HealthDetails(
        status="ok",
        recipes_loaded=len(recommender.recipes),
        embeddings_ready=recommender.embeddings is not None,
        model_name="all-MiniLM-L6-v2",
        users=counts["users"],
        recipes=counts["recipes"],
        ratings=counts["ratings"],
        saved_recipes=counts["saved_recipes"],
        feedback_entries=counts["feedback_entries"],
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)