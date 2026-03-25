from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, recipes, recommend
import uvicorn

app = FastAPI(title="Recipe Recommender API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommend"])

@app.get("/")
def read_root():
    return {"message": "Recipe Recommender API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)