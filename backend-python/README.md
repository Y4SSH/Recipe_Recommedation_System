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
- Vector search with FAISS
- No external API dependencies
- FastAPI with automatic OpenAPI docs

## API Endpoints

- `POST /recommend` - Get recipe recommendations
- `GET /recipes` - List recipes
- `POST /auth/register` - User registration
- `POST /auth/login` - User login