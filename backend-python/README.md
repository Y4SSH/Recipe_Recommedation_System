# Recipe Recommender Backend (Python)

A FastAPI-based backend for recipe recommendations using local AI models.

## Setup

1. Install Python 3.8+
2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Import data:
   ```bash
   python import_data.py
   ```
5. Run server:
   ```bash
   python -m app.main
   ```

## Features

- Local AI recommendations using sentence transformers
- No external API dependencies
- FastAPI with automatic OpenAPI docs
- Saved recipes API
- Ratings API with per-recipe summary
- Feedback API for recommendation outcomes
- User profile update endpoint
- Health and system details endpoint

## API Endpoints

- `POST /recommend/` - Get recipe recommendations
- `POST /recommend/reload` - Reload recommender embeddings (auth required)
- `GET /recipes/` - List recipes
- `GET /recipes/{recipe_id}` - Get recipe by id
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile
- `PATCH /auth/me` - Update current user profile
- `GET /saved/` - Get current user's saved recipes
- `POST /saved/{recipe_id}` - Save a recipe
- `DELETE /saved/{recipe_id}` - Remove a saved recipe
- `POST /ratings/` - Create or update a rating for a recipe
- `GET /ratings/me` - Get current user's ratings
- `GET /ratings/recipe/{recipe_id}` - Get rating summary for a recipe
- `POST /feedback/` - Submit recommendation feedback
- `GET /feedback/me` - Get current user's feedback
- `GET /health` - Basic health check
- `GET /health/details` - Health check with model/database counters