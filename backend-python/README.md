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
    python import_data.py --csv ../recipes_extended.csv --batch-size 2000
   ```
    The importer now prints total time and recipes/sec so you can estimate larger dataset switch times quickly.
   For safer large-dataset switching with rollback support, prefer:
   ```powershell
   .\switch_dataset.ps1 -CsvPath ..\recipes_extended.csv -BatchSize 2000
   ```
   ```cmd
   switch_dataset.cmd ..\recipes_extended.csv 2000
   ```
   This imports into a temporary DB first and swaps only after success.
   Optional image enrichment (Wikimedia title-based search):
   ```bash
   python enrich_recipe_images.py --limit 5000 --sleep-ms 50
   ```
5. Run server:
   ```bash
   python -m app.main
   ```

## Quick Run (Windows)

- One command via cmd:
   ```cmd
   run_backend.cmd
   ```
- Or via PowerShell:
   ```powershell
   .\run_backend.ps1
   ```
- Custom port:
   ```cmd
   run_backend.cmd 8001
   ```
   ```powershell
   .\run_backend.ps1 -Port 8001
   ```

## Dataset Swap And Rollback (Windows)

- Stop backend before swapping to avoid file lock issues on `recipes.db`.
- Swap to a new CSV safely:
   ```powershell
   .\switch_dataset.ps1 -CsvPath ..\recipes_extended.csv -BatchSize 2000
   ```
   ```cmd
   switch_dataset.cmd ..\recipes_extended.csv 2000
   ```
- One-click rollback to previous dataset:
   ```powershell
   .\switch_dataset.ps1 -Rollback
   ```
   ```cmd
   switch_dataset.cmd rollback
   ```
- User accounts are preserved automatically during swap.
- Backups are written to `backend-python\db_backups\` before each swap.

## Features

- Local AI recommendations using sentence transformers
- No external API dependencies
- FastAPI with automatic OpenAPI docs
- Saved recipes API
- Ratings API with per-recipe summary
- Feedback API for recommendation outcomes
- User profile update endpoint
- Health and system details endpoint

## Performance Tuning

- `RECOMMENDER_WARMUP_ON_STARTUP`:
   - Default: `1`
   - Set to `0` to skip embedding warmup at API startup.
- `RECOMMENDER_WARMUP_BATCH_SIZE`:
   - Default: `256`
   - Controls how many recipes are embedded per warmup batch.
   - Increase for faster total warmup on stronger machines, decrease to reduce startup memory pressure.

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