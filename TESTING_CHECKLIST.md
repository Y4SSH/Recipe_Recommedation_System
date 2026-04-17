# Quick Testing Checklist

Print this page or keep it open while testing. Check off each item as you complete it.

---

## Pre-Flight Checks (Do First)

- [ ] Backend running on `http://localhost:8000` 
  - Verify: `curl http://localhost:8000/health`
  - Should see: `{"status":"healthy"}`

- [ ] Frontend running on `http://localhost:5173`
  - Verify: Open in browser
  - Should see: Landing page

- [ ] Backend detailed health:
  - Verify: `curl http://localhost:8000/health/details`
  - Should see: recipe count ~1500, embeddings_cached=true/false

---

## API Testing (Backend)

### Authentication
- [ ] **Signup**: POST `/auth/register`
  - Email: `test@example.com`, Password: `Test123!`
  - Expected: 200 OK, user ID returned

- [ ] **Login**: POST `/auth/login`
  - Same email/password
  - Expected: 200 OK, JWT token returned
  - **👉 SAVE THIS TOKEN for remaining tests**

- [ ] **Get Profile**: GET `/auth/me`
  - Header: `Authorization: Bearer {TOKEN}`
  - Expected: 200 OK, email matches

### Recipes
- [ ] **List Recipes**: GET `/recipes/?limit=10`
  - Expected: 200 OK, 10 recipes with metadata fields
  - Verify fields: `variant_type`, `cooking_method`, `protein_type`, `base_recipe`

- [ ] **Filter by Cuisine**: GET `/recipes/?cuisine=indian&limit=5`
  - Expected: All recipes have `cuisine: "indian"`

- [ ] **Filter by Diet**: GET `/recipes/?diet=veg&limit=5`
  - Expected: All recipes have `diet: "veg"`

- [ ] **Get Recipe Detail**: GET `/recipes/{recipe_id}`
  - Use a recipe ID from list above
  - Expected: 200 OK, full details with ingredients, steps, metadata

### Recommendations
- [ ] **Get Recommendations**: POST `/recommend/`
  - Header: `Authorization: Bearer {TOKEN}`
  - Body: `{"ingredients":["potato","onion","tomato"]}`
  - Expected: 200 OK, array of scored recipes with explanations

- [ ] **Zero-Overlap Fallback**: POST `/recommend/`
  - Body: `{"ingredients":["fake_ingredient_xyz","qwerty"]}`
  - Expected: 200 OK, results with "broadened search" in explanation

- [ ] **Recommendation Stats**: GET `/recommend/stats`
  - Header: `Authorization: Bearer {TOKEN}`
  - Expected: 200 OK, stats show total recipes, users, embeddings cached

### Saved Recipes
- [ ] **Save a Recipe**: POST `/saved/{recipe_id}`
  - Header: `Authorization: Bearer {TOKEN}`
  - Expected: 200/201 Created

- [ ] **Get Saved Recipes**: GET `/saved/`
  - Header: `Authorization: Bearer {TOKEN}`
  - Expected: 200 OK, array includes recipe you just saved

### Ratings & Feedback
- [ ] **Rate a Recipe**: POST `/ratings/`
  - Header: `Authorization: Bearer {TOKEN}`
  - Body: `{"recipe_id":"{recipe_id}","score":4}`
  - Expected: 200 OK

- [ ] **Submit Feedback**: POST `/feedback/`
  - Header: `Authorization: Bearer {TOKEN}`
  - Body: `{"recommended_recipe_id":"{recipe_id}","accepted":true}`
  - Expected: 200 OK

---

## Frontend Testing (UI)

### Landing & Auth
- [ ] Landing page loads, shows Login/Signup buttons
- [ ] Signup form works, redirects to dashboard/login
- [ ] Login form works, stores token, redirects to dashboard

### Dashboard
- [ ] Page loads with search interface
- [ ] **Cuisine filter**: Shows exactly 2 options ✅
  - "Any (Indian dataset)"
  - "Indian"
  - ❌ NOT 16 options
  - ❌ NOT generic cuisines

- [ ] **Diet filter**: Shows Veg/Non-Veg chips
- [ ] **Ingredient search**: Autocomplete works
- [ ] **Search executes**: Results display with metadata visible

### Explore Page
- [ ] Page loads with recipe cards
- [ ] Each card shows: name, image, cuisine, diet, prep time
- [ ] **Cuisine section**: Shows only Indian option (not 8 cards)
- [ ] Clicking recipe opens detail page

### Recipe Detail Page
- [ ] Page loads
- [ ] **Hero section** shows: name, image, cuisine, diet label
- [ ] **Metadata tags** display (scroll down if needed):
  - [ ] Variant Type (e.g., "Main", "Side", "Appetizer")
  - [ ] Cooking Method (e.g., "Stir Fry", "Bake", "Grill")
  - [ ] Protein Type (e.g., "Vegetarian", "Chicken", "Fish")
  - [ ] Base Recipe (e.g., "Aloo Gobi")
- [ ] **Quick Info** shows: prep time, cook time, difficulty, servings, metadata
- [ ] **Ingredients** list displays with quantities
- [ ] **Steps** list displays numbered
- [ ] **Save Recipe** button works, shows confirmation
- [ ] **Rating stars** work, shows confirmation

### Saved Recipes
- [ ] Page loads
- [ ] Shows all recipes you saved
- [ ] Clicking recipe opens detail page
- [ ] Delete button works

### Recommendations
- [ ] Page loads with form
- [ ] **Form fields**: Ingredients input, Diet dropdown, Mode dropdown
- [ ] **Get Recommendations** button works
- [ ] Results display with: recipe name, score, explanation, image
- [ ] **Zero-overlap test**: Enter fake ingredients
  - [ ] Results still show (not empty)
  - [ ] **Alert box** appears: "Search was broadened..."
  - [ ] Explanations mention "broadened search"

- [ ] **Diet labels** are consistent:
  - [ ] When selecting "Veg", all results show veg label
  - [ ] No mixed terminology

---

## Edge Cases

- [ ] **Invalid login**: Wrong password shows error, doesn't login ✅
- [ ] **Duplicate email**: Signup shows error ✅
- [ ] **Empty search**: Shows validation error or all recipes ✅
- [ ] **Very long ingredient list**: Processes without timeout ✅
- [ ] **Non-existent recipe ID**: Shows "not found" error ✅
- [ ] **Logout & protected routes**: Redirected to login ✅
- [ ] **Special characters in search**: Handled gracefully ✅
- [ ] **Missing images**: Card still displays with fallback ✅

---

## Performance Checks

### WITHOUT Warmup (`RECOMMENDER_WARMUP_ON_STARTUP=0`)
- [ ] Backend startup time: _____ seconds
- [ ] First recommendation request: _____ ms (expect 800-2000 ms)
- [ ] Second recommendation request: _____ ms (expect 300-1000 ms)

### WITH Warmup (`RECOMMENDER_WARMUP_ON_STARTUP=1`)
- [ ] Backend startup + warmup time: _____ seconds (expect +10-15s)
- [ ] First recommendation request: _____ ms (expect 300-1000 ms, no cold penalty)

---

## Critical Success Criteria

### MUST PASS (Blockers):
- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Login/Signup flow works
- [ ] Recommendations API returns results
- [ ] No console errors (check DevTools)
- [ ] Cuisine filter shows ONLY 2 Indian options
- [ ] Metadata (variant_type, cooking_method, etc.) visible on recipe detail

### SHOULD PASS (Important):
- [ ] All API endpoints tested return 200/201
- [ ] Fallback logic works (zero-overlap returns results)
- [ ] Diet labels consistent across all pages
- [ ] Save recipe, rate recipe, feedback features work
- [ ] Both with/without warmup scenarios work

### NICE TO HAVE:
- [ ] Image loading optimized
- [ ] Response times within benchmarks
- [ ] UI feels responsive (<1s for most operations)

---

## Test Data You'll Need

Save these as you go:

- **Test User Email**: ________________________
- **Test User Password**: ________________________
- **JWT Token** (save from login): ________________________
- **Test Recipe ID**: ________________________
- **Test Saved Recipe ID**: ________________________

---

## Quick Links to Endpoints

**Test Ingredient:** `potatoes, onions, tomatoes`  
**Test Fake Ingredient:** `xyz_ingredient_fake, qwerty_notreal`  
**Test Diet:** `veg` or `non-veg`  
**Test Cuisine:** `indian`

---

**PASSED ALL TESTS?** ✅  
If yes, your AI Chef app is production-ready!  
If no, see troubleshooting section in MANUAL_TESTING_GUIDE.md
