# Recipe Recommendation System 🍳

A full-stack web application that provides personalized recipe recommendations using AI-powered search and intelligent recommendation engine. The system allows users to discover, save, and rate recipes with support for dietary preferences and cooking methods.

**Repository:** [Recipe_Recommedation_System](https://github.com/Y4SSH/Recipe_Recommedation_System.git)

---

## 🎯 Project Overview

This is a comprehensive recipe discovery and recommendation platform built with modern web technologies. The system features:
- **AI-Powered Recommendations:** Uses sentence transformers and FAISS for semantic recipe similarity
- **User Authentication:** Secure signup and login with JWT tokens
- **Recipe Management:** Browse, search, save, rate, and manage recipes
- **Personalized Experience:** Recommendations based on preferences and saved recipes
- **Rich Recipe Data:** 5,938+ Indian recipes with metadata including cooking methods, dietary types, and variants
- **Responsive UI:** Mobile-friendly interface built with React and Vite

---

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **AI/ML:** Sentence Transformers, FAISS for embeddings and semantic search
- **Authentication:** JWT with python-jose and passlib
- **API Documentation:** OpenAPI/Swagger
- **Server:** Uvicorn

### Frontend
- **Framework:** React 19.2.4
- **Build Tool:** Vite 8.0.1
- **Routing:** React Router v7
- **UI Components:** Lucide React (icons)
- **Styling:** CSS3

### DevOps
- **Containerization:** Docker and Docker Compose
- **Version Control:** Git/GitHub

---

## 📁 Project Structure

```
Major-Project/
├── backend-python/              # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app initialization and CORS setup
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── schemas.py          # Pydantic request/response schemas
│   │   ├── database.py         # Database connection and session management
│   │   ├── crud.py             # Database CRUD operations
│   │   ├── security.py         # JWT authentication logic
│   │   ├── recommender.py      # AI recommendation engine
│   │   ├── image_utils.py      # Image processing utilities
│   │   ├── food_classifier.py  # Food classification logic
│   │   └── routes/             # API route handlers
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── recipes.py      # Recipe CRUD endpoints
│   │       ├── recommend.py    # Recommendation endpoints
│   │       ├── saved.py        # Saved recipes endpoints
│   │       ├── my_recipes.py   # User recipes endpoints
│   │       ├── ratings.py      # Recipe ratings endpoints
│   │       └── feedback.py     # Feedback collection endpoints
│   ├── recipes.db              # SQLite database (5,938 recipes)
│   ├── requirements.txt        # Python dependencies
│   ├── run_backend.ps1         # PowerShell startup script
│   ├── run_backend.cmd         # CMD startup script
│   └── switch_dataset.ps1      # Dataset switching with rollback
├── frontend/                    # React/Vite frontend
│   ├── src/
│   │   ├── pages/              # React page components
│   │   │   ├── Landing.jsx     # Welcome/intro page
│   │   │   ├── Login.jsx       # User login
│   │   │   ├── Register.jsx    # User registration
│   │   │   ├── Dashboard.jsx   # Main recommendation interface
│   │   │   ├── Explore.jsx     # Recipe discovery/browsing
│   │   │   ├── RecipeDetailPage.jsx # Full recipe view
│   │   │   ├── Recommendations.jsx  # AI recommendations display
│   │   │   ├── SavedRecipes.jsx     # User's saved recipes
│   │   │   ├── MyRecipes.jsx    # User's personal recipes
│   │   │   ├── Profile.jsx      # User profile management
│   │   │   └── Auth.jsx         # Auth pages styling
│   │   ├── components/         # Reusable UI components
│   │   ├── context/            # React context for state management
│   │   ├── services/           # API client services
│   │   ├── styles/             # Global stylesheets
│   │   └── App.jsx             # Main app component
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml          # Multi-container setup
├── README.md                   # This file
└── requirements.txt            # Project dependencies
```

---

## 🚀 Features Implemented

### Authentication & User Management
- ✅ User registration with email validation
- ✅ Secure login with JWT tokens
- ✅ User profile management
- ✅ Password hashing with bcrypt

### Recipe Management
- ✅ Browse 5,938+ Indian recipes
- ✅ Search recipes by name, ingredients, cuisine
- ✅ Filter by cuisine type and dietary preferences
- ✅ View detailed recipe information (ingredients, steps, cooking time, servings)
- ✅ Recipe metadata display (cooking method, protein type, variant type, base recipe)

### AI Recommendations
- ✅ Semantic recipe recommendations using Sentence Transformers
- ✅ FAISS-based similarity search for fast retrieval
- ✅ Personalized recommendations based on saved recipes
- ✅ Fallback recommendations for cold-start users

### User Interactions
- ✅ Save/unsave recipes for later
- ✅ Rate recipes (1-5 stars)
- ✅ View rating aggregates (average score, total ratings)
- ✅ Provide feedback on recommendations
- ✅ View personal recipe collection

### UI/UX Features
- ✅ Responsive mobile-friendly design
- ✅ Real-time search with debouncing
- ✅ Toast notifications for user feedback
- ✅ Loading states and error handling
- ✅ Dietary preference filters (Vegetarian/Non-vegetarian)
- ✅ Cuisine filtering (Indian, Fusion, etc.)

---

## 📊 Database Schema

### Core Tables
- **Users:** User accounts, emails, hashed passwords
- **Recipes:** Recipe details (name, ingredients, steps, cooking time, servings)
- **Recipe Metadata:** Cooking methods, dietary types, protein types, variants
- **Saved Recipes:** User-saved recipe relationships
- **Ratings:** Recipe ratings with user and score
- **Feedback:** Recommendation feedback for model improvement
- **User Profiles:** Extended user information (preferences, dietary restrictions)

### Key Fields in Recipes
- `name`: Recipe name
- `ingredients`: JSON array of ingredients
- `instructions`: Cooking steps
- `diet_label`: Vegetarian/Non-vegetarian classification
- `cooking_time`: Time to prepare (minutes)
- `servings`: Number of servings
- `variant_type`: Recipe variant (e.g., "Mild", "Spicy")
- `cooking_method`: Preparation method
- `protein_type`: Primary protein source
- `base_recipe`: Reference to base recipe if variant
- `image_url`: Recipe image link

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Docker (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend-python
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   # The database is pre-populated with 5,938 recipes
   python -m app.main
   ```

5. **Run backend server:**
   ```bash
   # Windows PowerShell
   .\run_backend.ps1
   
   # Windows CMD
   run_backend.cmd
   
   # Or manually
   python -m app.main
   ```
   Backend runs on: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file (.env.local):**
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on: `http://localhost:5173`

5. **Build for production:**
   ```bash
   npm run build
   ```

---

## 🐳 Docker Setup

Run both backend and frontend with Docker Compose:

```bash
# Build and start containers
docker-compose up --build

# Run in background
docker-compose up -d

# Stop containers
docker-compose down
```

Accessible at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh JWT token

### Recipes
- `GET /recipes/` - Get all recipes (paginated)
- `GET /recipes/{id}` - Get recipe by ID
- `GET /recipes/search?q=...` - Search recipes by name/ingredients
- `GET /recipes/filter?diet=...&cuisine=...` - Filter recipes

### Recommendations
- `POST /recommend/` - Get AI-powered recommendations
- `GET /recommend/history` - Get recommendation history

### Saved Recipes
- `POST /saved/` - Save a recipe
- `GET /saved/` - Get user's saved recipes
- `DELETE /saved/{recipe_id}` - Remove saved recipe

### Ratings
- `POST /ratings/` - Add/update recipe rating
- `GET /ratings/{recipe_id}` - Get recipe rating stats
- `DELETE /ratings/{recipe_id}` - Remove rating

### Feedback
- `POST /feedback/` - Submit recommendation feedback

### User Profile
- `GET /my-recipes/profile` - Get user profile
- `PUT /my-recipes/profile` - Update user profile

---

## 🤖 AI Recommendation Engine

The recommendation system uses:
- **Sentence Transformers:** Converts recipes to semantic embeddings
- **FAISS:** Fast similarity search for finding related recipes
- **Semantic Search:** Matches recipes based on ingredients, cuisine, and cooking style
- **Personalization:** Considers user's saved recipes and ratings
- **Fallback Strategy:** Provides quality recommendations for new users

### How It Works
1. Recipe embeddings pre-computed at startup
2. User query/preferences embedded using same model
3. FAISS searches for top-K similar recipes
4. Results ranked by relevance score
5. Personalization layer applies user preferences

---

## 📱 Frontend Pages

1. **Landing Page** - Project introduction and call-to-action
2. **Login/Register** - User authentication
3. **Dashboard** - Main interface with recommendation filters
4. **Explore** - Browse and discover recipes with advanced filters
5. **Recipe Detail** - Complete recipe view with metadata, ratings, save option
6. **Recommendations** - AI-powered recommendations with filters
7. **Saved Recipes** - User's personal recipe collection
8. **My Recipes** - User's contributed recipes
9. **Profile** - User settings and preferences

---

## 🧪 Testing

Comprehensive testing documentation available:
- **MANUAL_TESTING_GUIDE.md** - Step-by-step testing procedures
- **API_TESTING_COMMANDS.md** - curl commands for API endpoints
- **BROWSER_CONSOLE_TESTING.md** - JavaScript utilities for frontend testing

### Running Tests
```bash
# Backend
cd backend-python
python -m pytest

# Frontend
cd frontend
npm run lint
npm run test
```

---

## 📊 Dataset Information

- **Total Recipes:** 5,938 Indian recipes
- **Data Format:** Recipe name, ingredients, instructions, cuisine, cooking time, servings, dietary info
- **Image Support:** Recipe images sourced from Wikimedia Commons
- **Metadata:** Includes variant types, cooking methods, protein classifications
- **Backup:** Cleaned_Indian_Food_Dataset.csv available for reference

---

## 🔄 Dataset Switching (with Rollback)

Switch to different recipe datasets safely:

```bash
# PowerShell (recommended - safer with rollback support)
cd backend-python
.\switch_dataset.ps1 -CsvPath ..\recipes_extended.csv -BatchSize 2000

# Rollback to previous dataset
.\switch_dataset.ps1 -Rollback

# Or CMD
switch_dataset.cmd ..\recipes_extended.csv 2000
switch_dataset.cmd rollback
```

**Note:** Stop the backend before switching datasets to avoid file locks.

---

## 🚢 Deployment

### GitHub
Repository is configured for GitHub deployment with:
- Size-optimized git history (large files purged)
- Standard .gitignore for Python and Node.js
- CI/CD ready structure

### Environment Variables
Backend (.env):
```
DATABASE_URL=sqlite:///./recipes.db
FRONTEND_URL=http://localhost:3000
RECOMMENDER_WARMUP_ON_STARTUP=1
RECOMMENDER_WARMUP_BATCH_SIZE=256
```

Frontend (.env.local):
```
VITE_API_URL=http://localhost:8000
```

---

## 📋 Recent Updates (April 2026)

✅ Frontend UI alignment - Simplified cuisine filters to 2 options (Indian-focused)
✅ Recipe metadata display - Added variant_type, cooking_method, protein_type tags on detail page
✅ Diet label normalization - Standardized display of vegetarian/non-vegetarian labels
✅ Comprehensive testing documentation - 4 detailed guides covering 100+ test scenarios
✅ Codebase cleanup - Removed 24 temporary files, freed ~150MB
✅ GitHub deployment - Fixed push issues, all code now under 100MB limit per file
✅ Database verification - 5,938 recipes confirmed working correctly

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is part of an academic/portfolio portfolio project.

---

## 📞 Support & Contact

For issues, questions, or suggestions:
- Create an Issue on GitHub
- Check existing documentation in backend-python/README.md
- Review test guides in root directory

---

## 🙏 Acknowledgments

- Indian Food Dataset for recipe data
- Sentence Transformers for NLP embeddings
- FAISS for similarity search
- FastAPI for robust backend framework
- React community for frontend resources

---

**Last Updated:** April 18, 2026
**Status:** Active Development ✅
**Database:** 5,938 recipes loaded
**API:** Fully functional with OpenAPI documentation