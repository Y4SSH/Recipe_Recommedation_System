# Manual Testing Guide - AI Chef Recipe Recommender

**Last Updated**: April 17, 2026  
**Testing Scope**: Backend API + Frontend UI + End-to-End Flows

---

## Table of Contents
1. [Pre-Testing Setup](#pre-testing-setup)
2. [Backend API Testing](#backend-api-testing)
3. [Frontend Testing](#frontend-testing)
4. [End-to-End User Flows](#end-to-end-user-flows)
5. [Edge Cases & Error Scenarios](#edge-cases--error-scenarios)
6. [Performance & Warmup Testing](#performance--warmup-testing)

---

## Pre-Testing Setup

### ✅ Step 1: Start the Backend

```bash
cd d:\Projects\Major-Project\backend-python
# Option A: With environment variables for warmup
set RECOMMENDER_WARMUP_ON_STARTUP=1
set RECOMMENDER_WARMUP_BATCH_SIZE=256
python main.py

# Option B: Without warmup (test cold start)
set RECOMMENDER_WARMUP_ON_STARTUP=0
python main.py
```

**Expected Output:**
- `INFO:     Uvicorn running on http://0.0.0.0:8000`
- `Warming up recommendation embeddings` (if warmup enabled)
- No error messages

**Wait For:**
- If warmup enabled: ~10-15 seconds for startup to complete (will see "Warmup complete")
- Backend ready when you see the Uvicorn startup message

---

### ✅ Step 2: Start the Frontend

In a new terminal:

```bash
cd d:\Projects\Major-Project\frontend
npm run dev
```

**Expected Output:**
- `VITE v4.x.x  ready in XXX ms`
- `Local: http://localhost:5173`
- No error messages

**Verify:** Open browser to `http://localhost:5173` - You should see the landing page (login/signup if not authenticated)

---

### ✅ Step 3: Verify Backend Health

**Test Endpoint:** Open your browser or use curl/Postman

```
GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-17T..."
}
```

**Test Detailed Health:**

```
GET http://localhost:8000/health/details
```

**Expected Response:**
```json
{
  "status": "healthy",
  "recipe_count": 1500,
  "embeddings_cached": true,
  "user_count": X,
  ...
}
```

---

## Backend API Testing

### 🧪 Test 1: User Signup

**Method:** POST  
**Endpoint:** `http://localhost:8000/auth/register`

**Request Body:**
```json
{
  "email": "testuser@example.com",
  "password": "securePassword123!"
}
```

**Expected Response:** `200 OK`
```json
{
  "email": "testuser@example.com",
  "id": "uuid-xxx"
}
```

**Verification Checklist:**
- ✅ Status code is 200
- ✅ Response contains user email
- ✅ Response contains user ID

**Edge Case:** Try duplicate email
```json
{
  "email": "testuser@example.com",
  "password": "anotherPassword"
}
```
**Expected:** `400` error with message about email already existing

---

### 🧪 Test 2: User Login

**Method:** POST  
**Endpoint:** `http://localhost:8000/auth/login`

**Request Body:**
```json
{
  "email": "testuser@example.com",
  "password": "securePassword123!"
}
```

**Expected Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "email": "testuser@example.com",
    "id": "uuid-xxx"
  }
}
```

**Verification Checklist:**
- ✅ Token returned is non-empty
- ✅ Token type is "bearer"
- ✅ User email matches request

**Save the token** for authenticated requests below.

---

### 🧪 Test 3: Get User Profile

**Method:** GET  
**Endpoint:** `http://localhost:8000/auth/me`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Expected Response:** `200 OK`
```json
{
  "email": "testuser@example.com",
  "id": "uuid-xxx",
  "name": null  // or user's name if updated
}
```

---

### 🧪 Test 4: List Recipes (Browse All)

**Method:** GET  
**Endpoint:** `http://localhost:8000/recipes/?limit=10`

**Expected Response:** `200 OK`
```json
{
  "total": 1500,
  "recipes": [
    {
      "id": "abc123",
      "name": "Aloo Gobi",
      "cuisine": "Indian",
      "diet": "veg",
      "prep_time": 15,
      "cook_time": 20,
      "difficulty": "easy",
      "image_url": "/static/recipes/aloo-gobi.jpg",
      "variant_type": "main",
      "cooking_method": "stir_fry",
      "protein_type": "vegetarian",
      "base_recipe": "Aloo Gobi"
    },
    ...
  ]
}
```

**Verification Checklist:**
- ✅ Returns array of recipes with at least 10 items
- ✅ Each recipe has required fields (id, name, cuisine, diet)
- ✅ Each recipe has enriched metadata (variant_type, cooking_method, protein_type)
- ✅ Image URLs are present

---

### 🧪 Test 5: Search Recipes by Cuisine

**Method:** GET  
**Endpoint:** `http://localhost:8000/recipes/?cuisine=indian&limit=10`

**Expected Response:** `200 OK`
- All returned recipes have `"cuisine": "indian"`
- At least 10 results

**Verification:** All recipes returned are Indian cuisine.

---

### 🧪 Test 6: Search Recipes by Diet

**Method:** GET  
**Endpoint:** `http://localhost:8000/recipes/?diet=veg&limit=10`

**Expected Response:** `200 OK`
- All returned recipes have `"diet": "veg"`

**Test Non-Veg:**
```
?diet=non-veg&limit=10
```
- All returned recipes have `"diet": "non-veg"`

---

### 🧪 Test 7: Get Single Recipe Details

**Method:** GET  
**Endpoint:** `http://localhost:8000/recipes/{recipe_id}`

Use a recipe ID from a previous list response.

**Expected Response:** `200 OK`
```json
{
  "id": "abc123",
  "name": "Aloo Gobi",
  "cuisine": "Indian",
  "diet": "veg",
  "prep_time": 15,
  "cook_time": 20,
  "difficulty": "easy",
  "servings": 4,
  "ingredients": [
    {
      "item": "potatoes",
      "quantity": 500,
      "unit": "g"
    },
    ...
  ],
  "steps": [
    "Heat oil in a pan",
    "Add potatoes and cauliflower",
    ...
  ],
  "variant_type": "main",
  "cooking_method": "stir_fry",
  "protein_type": "vegetarian",
  "base_recipe": "Aloo Gobi",
  "image_url": "/static/recipes/aloo-gobi.jpg"
}
```

---

### 🧪 Test 8: Get Recommendations (Basic - With Ingredients)

**Method:** POST  
**Endpoint:** `http://localhost:8000/recommend/`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Request Body:**
```json
{
  "ingredients": ["potatoes", "onions", "tomatoes"],
  "user_id": "uuid-xxx-optional",
  "mode": "balanced"
}
```

**Expected Response:** `200 OK`
```json
{
  "recommendations": [
    {
      "id": "recipe-id-1",
      "name": "Recipe Name 1",
      "score": 0.85,
      "explanation": "Contains 3/4 of your ingredients",
      "image_url": "/static/recipes/...",
      "diet": "veg",
      ...
    },
    ...
  ]
}
```

**Verification Checklist:**
- ✅ Returns array of recommendations
- ✅ Each recommendation has a score (0-1)
- ✅ Each recommendation has explanation text
- ✅ Recipes are relevant to input ingredients

---

### 🧪 Test 9: Get Recommendations (Zero-Overlap Fallback)

**Request Body:**
```json
{
  "ingredients": ["xyz_ingredient_that_doesnt_exist", "qwerty_fake_ingredient"],
  "mode": "balanced"
}
```

**Expected Response:** `200 OK` with fallback behavior
```json
{
  "recommendations": [
    {
      "id": "recipe-id-1",
      "name": "Recipe Name",
      "score": 0.72,
      "explanation": "No exact ingredient matches found. Search was broadened to similar recipes.",
      ...
    },
    ...
  ]
}
```

**Verification Checklist:**
- ✅ Still returns recommendations (doesn't return empty array)
- ✅ Explanation contains "broadened" or "similar"
- ✅ Results are diverse (not all from one cuisine)

---

### 🧪 Test 10: Save a Recipe

**Method:** POST  
**Endpoint:** `http://localhost:8000/saved/{recipe_id}`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Expected Response:** `200 OK` or `201 Created`
```json
{
  "id": "saved-id",
  "user_id": "uuid-xxx",
  "recipe_id": "recipe-id",
  "created_at": "2026-04-17T..."
}
```

---

### 🧪 Test 11: Get Saved Recipes

**Method:** GET  
**Endpoint:** `http://localhost:8000/saved/`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Expected Response:** `200 OK`
```json
{
  "total": 3,
  "saved_recipes": [
    {
      "id": "recipe-id-1",
      "name": "Aloo Gobi",
      ...
    }
  ]
}
```

---

### 🧪 Test 12: Rate a Recipe

**Method:** POST  
**Endpoint:** `http://localhost:8000/ratings/`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Request Body:**
```json
{
  "recipe_id": "recipe-id-1",
  "score": 4
}
```

**Expected Response:** `200 OK`
```json
{
  "id": "rating-id",
  "recipe_id": "recipe-id-1",
  "user_id": "uuid-xxx",
  "score": 4
}
```

---

### 🧪 Test 13: Submit Feedback on Recommendation

**Method:** POST  
**Endpoint:** `http://localhost:8000/feedback/`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Request Body:**
```json
{
  "recommended_recipe_id": "recipe-id-1",
  "accepted": true,
  "notes": "Great recipe, loved it!"
}
```

**Expected Response:** `200 OK`
```json
{
  "id": "feedback-id",
  "user_id": "uuid-xxx",
  "recommended_recipe_id": "recipe-id-1",
  "accepted": true,
  "notes": "Great recipe, loved it!"
}
```

---

### 🧪 Test 14: Get Recommendation Stats

**Method:** GET  
**Endpoint:** `http://localhost:8000/recommend/stats`  
**Headers:**
```
Authorization: Bearer {YOUR_TOKEN}
```

**Expected Response:** `200 OK`
```json
{
  "total_recipes": 1500,
  "total_users": X,
  "embeddings_cached": true,
  "warmup_enabled": true,
  "total_ratings": Y,
  "total_feedback": Z
}
```

---

## Frontend Testing

### 📱 Test 1: Landing Page (Unauthenticated)

**Steps:**
1. Navigate to `http://localhost:5173`
2. Verify you see the landing page with two buttons: **Login** and **Sign Up**

**Verification Checklist:**
- ✅ Page loads without errors
- ✅ Login button visible
- ✅ Sign Up button visible
- ✅ No console errors

---

### 📱 Test 2: Signup Flow

**Steps:**
1. Click **Sign Up** button
2. Enter email: `testuser@example.com`
3. Enter password: `securePassword123!`
4. Click **Create Account**

**Verification Checklist:**
- ✅ Form submits successfully
- ✅ No validation errors appear
- ✅ Redirected to Dashboard (or Login page)
- ✅ No console errors

---

### 📱 Test 3: Login Flow

**Steps:**
1. Navigate to `http://localhost:5173`
2. Click **Login**
3. Enter email: `testuser@example.com`
4. Enter password: `securePassword123!`
5. Click **Sign In**

**Verification Checklist:**
- ✅ Form submits successfully
- ✅ Token is saved (check localStorage: key = `authToken`)
- ✅ Redirected to Dashboard
- ✅ Dashboard shows user's information

---

### 📱 Test 4: Dashboard - Recipe Search

**Steps:**
1. On Dashboard, look at the **Cuisine Filter** dropdown
2. Verify it shows: **"Any (Indian dataset)"** and **"Indian"** options
3. Select **"Indian"**

**Verification Checklist:**
- ✅ Only 2 cuisine options visible (Indian-focused)
- ✅ Selecting Indian applies filter
- ✅ Results update accordingly

---

### 📱 Test 5: Dashboard - Ingredient Search

**Steps:**
1. On Dashboard, find the **Ingredient Input** field
2. Type: `potatoes`
3. Press Enter or click Search

**Verification Checklist:**
- ✅ Autocomplete suggestions appear
- ✅ Search executes
- ✅ Results display below

---

### 📱 Test 6: Dashboard - Diet Filter

**Steps:**
1. On Dashboard, look for **Diet** filter options
2. Verify options show: **Veg** and **Non-Veg** chips
3. Click **Veg**

**Verification Checklist:**
- ✅ Diet chips visible and clickable
- ✅ Veg filter applied
- ✅ Results update to show only vegetarian recipes
- ✅ Chip shows as selected (different styling)

---

### 📱 Test 7: Explore Page - Browse Recipes

**Steps:**
1. Click **Explore** in navigation
2. Page loads and shows recipe cards

**Verification Checklist:**
- ✅ Recipe cards display with images
- ✅ Each card shows: name, cuisine, diet, prep time
- ✅ Cards are clickable
- ✅ No console errors

---

### 📱 Test 8: Explore Page - Cuisine Filter

**Steps:**
1. On Explore page, check the cuisine section
2. Verify only **"Indian"** option is shown
3. Click it

**Verification Checklist:**
- ✅ Only 1 Indian option visible (simplified from old 16 options)
- ✅ Clicking applies filter
- ✅ Recipe results are all Indian cuisine

---

### 📱 Test 9: Recipe Detail Page - Metadata Display

**Steps:**
1. Click on any recipe card (from Explore or search results)
2. Recipe detail page opens
3. Scroll to view the recipe information

**Verification Checklist:**
- ✅ Hero section shows: image, name, cuisine, diet
- ✅ Below hero, see **enriched metadata tags**: 
  - Variant Type (e.g., "Main", "Side", "Dessert")
  - Cooking Method (e.g., "Stir Fry", "Bake")
  - Protein Type (e.g., "Vegetarian", "Chicken")
  - Base Recipe (e.g., "Aloo Gobi")
- ✅ Quick info section shows: prep time, cook time, difficulty, servings
- ✅ Ingredients list displays with quantities
- ✅ Steps list displays with numbered instructions

---

### 📱 Test 10: Recipe Detail - Save Recipe

**Steps:**
1. On Recipe Detail page, find the **"Save Recipe"** button
2. Click it

**Verification Checklist:**
- ✅ Button changes appearance (e.g., turns blue or shows "Saved")
- ✅ Toast notification shows "Recipe saved!"
- ✅ Recipe is added to Saved Recipes collection

---

### 📱 Test 11: Recipe Detail - Rate Recipe

**Steps:**
1. On Recipe Detail page, find the **Rating** section (stars)
2. Click on the 4th star to rate 4/5

**Verification Checklist:**
- ✅ Stars highlight up to selected rating
- ✅ Toast notification shows rating submitted
- ✅ Rating persists (reload page and it's still shown)

---

### 📱 Test 12: Saved Recipes Collection

**Steps:**
1. Click **Saved Recipes** in navigation
2. Page loads showing your saved recipes

**Verification Checklist:**
- ✅ All recipes you saved are displayed
- ✅ Each recipe card shows: name, image, diet, cuisine
- ✅ Clicking a card opens Recipe Detail page
- ✅ Delete button removes from collection

---

### 📱 Test 13: Recommendations Page - Get Recommendations

**Steps:**
1. Click **Get Recommendations** in navigation
2. Page displays form with fields:
   - Ingredients input
   - Diet preference
   - Recommendation mode
3. Enter ingredients: `"potatoes, onions, tomatoes"`
4. Select Diet: **Veg**
5. Select Mode: **Balanced**
6. Click **Get Recommendations**

**Verification Checklist:**
- ✅ Form submits successfully
- ✅ Loading spinner appears briefly
- ✅ Recommendations display with cards
- ✅ Each card shows: recipe name, score (%), explanation, image
- ✅ Cards are clickable

---

### 📱 Test 14: Recommendations Page - Fallback Notice

**Steps:**
1. On Recommendations page, enter fake ingredients: `"xyz_ingredient_fake, qwerty_notreal"`
2. Click **Get Recommendations**

**Verification Checklist:**
- ✅ Results load (not empty)
- ✅ **Alert box** appears above results with text like:
  > "No exact ingredient matches found. Search was broadened to show similar recipes."
- ✅ Recommendations are displayed despite zero overlap
- ✅ Explanation in cards reflects the broadened search

---

### 📱 Test 15: Recommendations Page - Diet Label Consistency

**Steps:**
1. Request recommendations with Diet: **Non-Veg**
2. Observe all recipe cards

**Verification Checklist:**
- ✅ All recipe cards show consistent "Non-Veg" or "Chicken" or similar labels
- ✅ No inconsistent terminology (e.g., "vegetarian" mixed with "non-veg")
- ✅ Labels match backend data

---

## End-to-End User Flows

### 🔄 Flow 1: Complete Recommendation Journey

**Scenario:** New user discovers and saves a recipe

**Steps:**
1. **Signup/Login** (Tests 1-3 from Backend, 2-3 from Frontend)
2. **Browse Recipes** (Frontend Test 7)
3. **Click Recipe** to view details (Frontend Test 9)
4. **View Metadata** and verify enriched fields (Frontend Test 9)
5. **Save Recipe** (Frontend Test 10)
6. **Rate Recipe** (Frontend Test 11)
7. **Navigate to Saved Recipes** (Frontend Test 12)
8. **Verify recipe appears** in collection

**Time Expected:** ~5-7 minutes  
**Success Criteria:** All steps complete without errors

---

### 🔄 Flow 2: AI Recommendation & Feedback Loop

**Scenario:** User gets AI recommendations and provides feedback

**Steps:**
1. **Login** to frontend
2. **Navigate to Recommendations** page
3. **Input ingredients**: `"garlic, ginger, cumin, coriander"`
4. **Select diet**: Veg
5. **Click Get Recommendations** (Backend Test 8)
6. **Observe fallback behavior** if needed (Backend Test 9)
7. **Click on a recommended recipe** (Frontend Test 9)
8. **Review recipe details** with enriched metadata
9. **Save the recipe** (Frontend Test 10)
10. **Return to Recommendations** and submit feedback

**Time Expected:** ~8-10 minutes  
**Success Criteria:** Recommendations appear, metadata visible, feedback submits

---

### 🔄 Flow 3: Search & Filter Journey

**Scenario:** User searches with filters to narrow results

**Steps:**
1. **Login** to frontend
2. **Go to Dashboard**
3. **Set Cuisine Filter** to Indian (Frontend Test 4)
4. **Set Diet Filter** to Veg (Frontend Test 6)
5. **Search Ingredient** (Frontend Test 5)
6. **Observe filtered results**
7. **Click result** to view details

**Time Expected:** ~3-5 minutes  
**Success Criteria:** Filters apply correctly, results are relevant and filtered

---

### 🔄 Flow 4: Warmup & Cold Start Performance

**Scenario:** Test recommendation latency with and without warmup

**Steps:**
1. **Start backend WITHOUT warmup**:
   ```bash
   set RECOMMENDER_WARMUP_ON_STARTUP=0
   python main.py
   ```
2. **Note startup completion time**
3. **Login to frontend**
4. **Navigate to Recommendations**
5. **Enter ingredients and click Get**
6. **Note time to first result** (should be ~0.3-1.5s for cold start)
7. **Submit another recommendation request**
8. **Note time to second result** (should be ~0.5-1.4s, warmed up)

Then:

9. **Restart backend WITH warmup**:
   ```bash
   set RECOMMENDER_WARMUP_ON_STARTUP=1
   python main.py
   ```
10. **Note startup completion time** (should add ~10-15 seconds for warmup)
11. **Repeat steps 4-8**
12. **Note first request time** (should be ~0.3-1.4s, already warmed)

**Time Expected:** ~15-20 minutes (including backend restarts)  
**Success Criteria:**
- With warmup off: Cold first request ~1-2s, second request ~0.5-1.4s
- With warmup on: Startup takes longer, but first request ~0.3-1.4s (no cold start penalty)

---

## Edge Cases & Error Scenarios

### ⚠️ Edge Case 1: Invalid Credentials

**Test:** Login with wrong password

**Steps:**
1. Frontend: Enter correct email but wrong password
2. Click Sign In

**Expected:**
- ✅ Error message appears: "Invalid credentials"
- ✅ User remains on login page
- ✅ No token stored in localStorage

---

### ⚠️ Edge Case 2: Duplicate Email Signup

**Test:** Try to register with existing email

**Steps:**
1. Frontend: Signup with `testuser@example.com` (already exists)
2. Click Create Account

**Expected:**
- ✅ Error message appears
- ✅ Form is not submitted
- ✅ User remains on signup page

---

### ⚠️ Edge Case 3: Empty Search

**Test:** Search with empty ingredients

**Steps:**
1. Frontend Dashboard: Leave Ingredient field empty
2. Click Search

**Expected:**
- ✅ Either: Shows all recipes OR shows validation error "Enter at least one ingredient"
- ✅ No crash or blank page

---

### ⚠️ Edge Case 4: Very Long Ingredient List

**Test:** Search with 20+ ingredients

**Steps:**
1. Frontend: Enter `"potato, onion, tomato, garlic, ginger, cumin, coriander, turmeric, chili, asafoetida, cinnamon, cardamom, cloves, bay leaf, salt, oil, water, coconut, cashew, raisin, almond"`
2. Click Search

**Expected:**
- ✅ Query processes (might take slightly longer)
- ✅ Results display
- ✅ No timeout or error

---

### ⚠️ Edge Case 5: Non-Existent Recipe ID

**Test:** Access recipe with fake ID

**Steps:**
1. Try: `http://localhost:5173/recipe/fake-id-xyz`

**Expected:**
- ✅ Page shows error: "Recipe not found"
- ✅ Link back to Explore or Dashboard

---

### ⚠️ Edge Case 6: Logout & Re-login

**Test:** Logout and verify session ends

**Steps:**
1. Frontend: Click Logout button
2. Verify redirected to landing page
3. Try to access `/dashboard` directly
4. Verify redirected to login

**Expected:**
- ✅ Token removed from localStorage
- ✅ Protected routes redirect to login
- ✅ No console errors

---

### ⚠️ Edge Case 7: Network Offline (Simulated)

**Test:** Use browser DevTools to simulate offline

**Steps:**
1. Open DevTools (F12)
2. Go to Network tab
3. Check "Offline" checkbox
4. Try to make a request (search, recommendations)

**Expected:**
- ✅ Error message appears: "Network error" or "Failed to connect"
- ✅ UI doesn't crash
- ✅ User can take corrective action (reload, check connection)

---

### ⚠️ Edge Case 8: Concurrent Recommendations

**Test:** Rapidly click "Get Recommendations" multiple times

**Steps:**
1. Frontend Recommendations page
2. Click "Get Recommendations" button
3. While loading, click again (3-4 times rapidly)

**Expected:**
- ✅ Only one request processes (or latest one wins)
- ✅ No duplicate results
- ✅ No console errors
- ✅ No race condition issues

---

### ⚠️ Edge Case 9: Special Characters in Search

**Test:** Search with special characters

**Steps:**
1. Frontend: Enter `"@#$%^&*()"` in search
2. Click Search

**Expected:**
- ✅ Backend handles gracefully (returns no results or error)
- ✅ Frontend doesn't crash
- ✅ Error message is user-friendly

---

### ⚠️ Edge Case 10: Image Not Found

**Test:** Browse recipes with missing images

**Steps:**
1. Check DevTools Network tab for failed image requests (404s)
2. Verify recipe cards still display with placeholder/default image

**Expected:**
- ✅ Fallback image displays (or no image but content still visible)
- ✅ Card layout doesn't break
- ✅ No broken image icons that confuse users

---

## Performance & Warmup Testing

### 📊 Test 1: Measure Cold Start Latency

**Setup:** Backend with `RECOMMENDER_WARMUP_ON_STARTUP=0`

**Steps:**
1. Start backend and note startup time
2. Login to frontend
3. Open DevTools → Network tab
4. Go to Recommendations page
5. Enter ingredients and submit
6. Look at Network tab → "recommend" API call
7. Note **Response time** in green

**Metrics to Record:**
- Backend startup time: _____ seconds
- First recommendation request: _____ ms
- Second recommendation request: _____ ms
- Fifth recommendation request: _____ ms

**Expected Values:**
- Backend startup: ~2-5 seconds
- First request: 1000-2000 ms (cold start)
- Second request: 500-1500 ms (warmed)
- Fifth request: 500-1500 ms (sustained)

---

### 📊 Test 2: Measure Warmup Benefits

**Setup:** Backend with `RECOMMENDER_WARMUP_ON_STARTUP=1`

**Steps:**
1. Start backend and note startup time
2. Wait for warmup to complete (will see message)
3. Login to frontend
4. Open DevTools → Network tab
5. Go to Recommendations page
6. Enter ingredients and submit
7. Note **Response time**

**Metrics to Record:**
- Backend startup + warmup time: _____ seconds
- First recommendation request: _____ ms
- Second recommendation request: _____ ms

**Expected Values:**
- Total startup: ~10-20 seconds (includes embedding precompute)
- First request: 300-1500 ms (no cold start penalty)
- Second request: 300-1500 ms (warmed already)

**Comparison:** Warmup startup takes longer, but eliminates cold start penalty on first user request.

---

### 📊 Test 3: API Response Time Benchmarks

Using DevTools Network tab or curl with timing:

**Test Each Endpoint:**

```bash
# Test recipes list (should be fast, no ML)
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/recipes/?limit=10

# Test single recipe (should be fast)
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/recipes/recipe_id_here

# Test recommendations (should be slower due to ML)
curl -X POST http://localhost:8000/recommend/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["potato","onion"]}' \
  -w "\nTime: %{time_total}s\n"
```

**Expected Benchmarks:**
- `GET /recipes/`: 50-200 ms
- `GET /recipes/{id}`: 30-100 ms
- `POST /recommend/`: 300-1500 ms (depends on warmup and cache state)
- `GET /saved/`: 50-150 ms
- `POST /feedback/`: 50-150 ms

---

## Checklist Summary

### Backend completeness:
- [ ] Health endpoint returns 200
- [ ] Auth signup works
- [ ] Auth login returns token
- [ ] All 14 API tests pass (Tests 1-14)
- [ ] Recommendations with ingredients work
- [ ] Zero-overlap fallback works
- [ ] Saved recipes work
- [ ] Ratings work
- [ ] Feedback works

### Frontend completeness:
- [ ] Landing page loads
- [ ] Signup flow works
- [ ] Login flow works
- [ ] Dashboard loads
- [ ] Cuisine filter shows 2 Indian options only
- [ ] Ingredient search works
- [ ] Diet filter shows Veg/Non-Veg
- [ ] Explore page displays recipes
- [ ] Recipe detail shows enriched metadata (variant, method, protein, base)
- [ ] Save recipe works
- [ ] Rate recipe works
- [ ] Saved recipes page loads
- [ ] Recommendations page works
- [ ] Fallback notice appears for zero-overlap
- [ ] Diet labels are consistent

### End-to-end flows:
- [ ] Complete recommendation journey (Flow 1)
- [ ] AI recommendation &feedback loop (Flow 2)
- [ ] Search & filter journey (Flow 3)
- [ ] Warmup benefits demonstrated (Flow 4)

### Edge cases:
- [ ] All 10 edge cases tested and handled gracefully
- [ ] No console errors
- [ ] No broken UI layouts
- [ ] Error messages are clear and actionable

### Performance:
- [ ] Cold start latency measured
- [ ] Warmup benefits verified
- [ ] API response times within expected ranges

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Backend won't start | Check port 8000 not in use: `netstat -anb` |
| Frontend won't start | Check port 5173 not in use |
| CORS errors | Verify CORS is enabled: Check `main.py` |
| Recommendation returns empty | Enable fallback or check ingredients exist in DB |
| Recipe images not loading | Check `/static/recipes/` directory exists |
| Auth failures | Verify JWT secret in `.env` |
| API timeout | Check warmup is enabled; give more time on first request |
| Metadata not showing | Hard refresh frontend (Ctrl+Shift+R) or clear cache |

---

## Notes

- All tests should be performed in order for best results
- Record timestamps and response times for performance baseline
- Screenshots of each major page are useful for documentation
- Test on different browsers if possible (Chrome, Firefox, Safari)
- Clear browser cache/localStorage between major test phases if needed

**Total Testing Time Estimate:** 2-3 hours for complete coverage

