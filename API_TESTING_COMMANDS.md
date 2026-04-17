# API Testing Commands

Use these curl commands to test the backend API. Run in PowerShell.

---

## Setup

**Save your token here after login:**
```powershell
$TOKEN = "YOUR_TOKEN_HERE"
$BASE_URL = "http://localhost:8000"
```

---

## Health Checks

### Basic Health
```powershell
curl "$BASE_URL/health"
```

**Expected Output:**
```json
{"status":"healthy","timestamp":"2026-04-17T..."}
```

### Detailed Health
```powershell
curl "$BASE_URL/health/details"
```

---

## Authentication

### Signup
```powershell
$SignupBody = @{
    email = "testuser@example.com"
    password = "securePassword123!"
} | ConvertTo-Json

curl -X POST "$BASE_URL/auth/register" `
  -ContentType "application/json" `
  -Body $SignupBody
```

### Login (Get Token)
```powershell
$LoginBody = @{
    email = "testuser@example.com"
    password = "securePassword123!"
} | ConvertTo-Json

curl -X POST "$BASE_URL/auth/login" `
  -ContentType "application/json" `
  -Body $LoginBody
```

**Save the `access_token` value from response to `$TOKEN`**

### Get Current User Profile
```powershell
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/auth/me"
```

### Update User Profile
```powershell
$UpdateBody = @{
    name = "Test User"
} | ConvertTo-Json

curl -X PATCH `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $UpdateBody `
  "$BASE_URL/auth/me"
```

### Get Pantry
```powershell
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/auth/pantry"
```

### Update Pantry
```powershell
$PantryBody = @{
    items = @(
        @{name = "potatoes"; expires_in_days = 7},
        @{name = "onions"; expires_in_days = 14},
        @{name = "tomatoes"; expires_in_days = 3}
    )
} | ConvertTo-Json

curl -X PUT `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $PantryBody `
  "$BASE_URL/auth/pantry"
```

---

## Recipes

### List All Recipes
```powershell
curl "$BASE_URL/recipes/?limit=10"
```

### List with Skip (Pagination)
```powershell
curl "$BASE_URL/recipes/?skip=0&limit=20"
```

### Search Recipes
```powershell
curl "$BASE_URL/recipes/?search=aloo"
```

### Filter by Cuisine
```powershell
curl "$BASE_URL/recipes/?cuisine=indian&limit=10"
```

### Filter by Diet
```powershell
curl "$BASE_URL/recipes/?diet=veg&limit=10"
```

### Filter by Multiple Criteria
```powershell
curl "$BASE_URL/recipes/?cuisine=indian&diet=veg&limit=10"
```

### Get Single Recipe (Replace {recipe_id})
```powershell
$recipe_id = "YOUR_RECIPE_ID_HERE"
curl "$BASE_URL/recipes/$recipe_id"
```

---

## Recommendations

### Get Recommendations (Basic)
```powershell
$RecommendBody = @{
    ingredients = @("potatoes", "onions", "tomatoes")
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $RecommendBody `
  "$BASE_URL/recommend/"
```

### Get Recommendations (With Mode)
```powershell
$RecommendBody = @{
    ingredients = @("potatoes", "onions", "tomatoes")
    mode = "balanced"
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $RecommendBody `
  "$BASE_URL/recommend/"
```

### Test Zero-Overlap Fallback
```powershell
$RecommendBody = @{
    ingredients = @("xyz_ingredient_fake", "qwerty_notreal")
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $RecommendBody `
  "$BASE_URL/recommend/"
```

**Should return results with "broadened search" in explanation**

### Recommendation Stats
```powershell
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/recommend/stats"
```

### Reload Recommendation Engine
```powershell
curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  "$BASE_URL/recommend/reload"
```

---

## Saved Recipes

### Get All Saved Recipes
```powershell
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/saved/"
```

### Save a Recipe (Replace {recipe_id})
```powershell
$recipe_id = "YOUR_RECIPE_ID_HERE"

curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  "$BASE_URL/saved/$recipe_id"
```

### Delete Saved Recipe
```powershell
$recipe_id = "YOUR_RECIPE_ID_HERE"

curl -X DELETE `
  -H "Authorization: Bearer $TOKEN" `
  "$BASE_URL/saved/$recipe_id"
```

---

## Ratings

### Rate a Recipe
```powershell
$RateBody = @{
    recipe_id = "YOUR_RECIPE_ID_HERE"
    score = 4
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $RateBody `
  "$BASE_URL/ratings/"
```

### Get My Ratings
```powershell
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/ratings/me"
```

### Get Rating Summary for Recipe
```powershell
$recipe_id = "YOUR_RECIPE_ID_HERE"

curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/ratings/recipe/$recipe_id"
```

---

## Feedback

### Submit Feedback on Recommendation
```powershell
$FeedbackBody = @{
    recommended_recipe_id = "YOUR_RECIPE_ID_HERE"
    accepted = $true
    notes = "Great recipe, loved it!"
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body $FeedbackBody `
  "$BASE_URL/feedback/"
```

### Get My Feedback
```powershell
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/feedback/me"
```

---

## Quick Test Script (Run All at Once)

```powershell
# 1. Health check
Write-Host "1. Health Check..."
curl "$BASE_URL/health" | ConvertFrom-Json | Format-Table
Write-Host ""

# 2. List recipes
Write-Host "2. List Recipes..."
curl "$BASE_URL/recipes/?limit=5" | ConvertFrom-Json | Format-Table
Write-Host ""

# 3. Filter by cuisine
Write-Host "3. Filter by Cuisine (Indian)..."
curl "$BASE_URL/recipes/?cuisine=indian&limit=3" | ConvertFrom-Json | Format-Table
Write-Host ""

# 4. Filter by diet
Write-Host "4. Filter by Diet (Veg)..."
curl "$BASE_URL/recipes/?diet=veg&limit=3" | ConvertFrom-Json | Format-Table
Write-Host ""

Write-Host "✅ Basic API tests completed!"
```

---

## Useful Variables to Save

After successful login:

```powershell
# Extract token from login response
$LoginResponse = curl -X POST "$BASE_URL/auth/login" `
  -ContentType "application/json" `
  -Body (@{email = "testuser@example.com"; password = "securePassword123!"} | ConvertTo-Json) | ConvertFrom-Json

$TOKEN = $LoginResponse.access_token
$USER_ID = $LoginResponse.user.id

# Extract recipe ID for testing
$Recipes = curl "$BASE_URL/recipes/?limit=1" | ConvertFrom-Json
$RECIPE_ID = $Recipes.recipes[0].id

Write-Host "Token: $TOKEN"
Write-Host "User ID: $USER_ID"
Write-Host "Recipe ID: $RECIPE_ID"
```

---

## Testing Scenarios (Copy-Paste Ready)

### Scenario 1: Full Signup → Login → Get Profile
```powershell
# 1. Signup
$SignupResp = curl -X POST "$BASE_URL/auth/register" `
  -ContentType "application/json" `
  -Body (@{email = "newuser$(Get-Date -f yyyyMMddHHmmss)@test.com"; password = "Pass123!"} | ConvertTo-Json) | ConvertFrom-Json

$NewEmail = $SignupResp.email
Write-Host "✅ Signed up as: $NewEmail"

# 2. Login
$LoginResp = curl -X POST "$BASE_URL/auth/login" `
  -ContentType "application/json" `
  -Body (@{email = $NewEmail; password = "Pass123!"} | ConvertTo-Json) | ConvertFrom-Json

$TOKEN = $LoginResp.access_token
Write-Host "✅ Logged in, token: $($TOKEN.Substring(0, 20))..."

# 3. Get Profile
$Profile = curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/auth/me" | ConvertFrom-Json
Write-Host "✅ Profile retrieved: $($Profile.email)"
```

### Scenario 2: Browse Recipes → Save → Get Saved
```powershell
# 1. Get recipes
$RecipesResp = curl "$BASE_URL/recipes/?limit=5" | ConvertFrom-Json
$RecipeToSave = $RecipesResp.recipes[0]
Write-Host "✅ Found recipe: $($RecipeToSave.name)"

# 2. Save recipe
curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  "$BASE_URL/saved/$($RecipeToSave.id)" | ConvertFrom-Json
Write-Host "✅ Saved recipe"

# 3. Get saved recipes
$Saved = curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/saved/" | ConvertFrom-Json
Write-Host "✅ Saved recipes count: $($Saved.total)"
```

### Scenario 3: Get Recommendations → Rate → Feedback
```powershell
# 1. Get recommendations
$RecommendResp = curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body (@{ingredients = @("potatoes", "onions", "tomatoes")} | ConvertTo-Json) `
  "$BASE_URL/recommend/" | ConvertFrom-Json

$RecipeToRate = $RecommendResp.recommendations[0]
Write-Host "✅ Got recommendation: $($RecipeToRate.name)"

# 2. Rate recipe
curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body (@{recipe_id = $RecipeToRate.id; score = 4} | ConvertTo-Json) `
  "$BASE_URL/ratings/" | ConvertFrom-Json
Write-Host "✅ Rated recipe: 4/5"

# 3. Submit feedback
curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body (@{recommended_recipe_id = $RecipeToRate.id; accepted = $true; notes = "Great recipe!"} | ConvertTo-Json) `
  "$BASE_URL/feedback/" | ConvertFrom-Json
Write-Host "✅ Feedback submitted"
```

---

## Timing Requests

To measure response times, add timing:

```powershell
# Single request timing
$StartTime = Get-Date
$Response = curl -X POST `
  -H "Authorization: Bearer $TOKEN" `
  -ContentType "application/json" `
  -Body (@{ingredients = @("potato", "onion")} | ConvertTo-Json) `
  "$BASE_URL/recommend/"
$TimeElapsed = (Get-Date) - $StartTime

Write-Host "Response time: $($TimeElapsed.TotalMilliseconds) ms"
```

---

## Error Handling

All responses should include status. Check for:

```powershell
# Try-catch for failures
try {
    $Response = curl -X POST "$BASE_URL/auth/login" `
      -ContentType "application/json" `
      -Body (@{email = "wrong@test.com"; password = "wrong"} | ConvertTo-Json)
    
    $Data = $Response | ConvertFrom-Json
    
    if ($null -ne $Data.error) {
        Write-Host "❌ Error: $($Data.error)"
    } else {
        Write-Host "✅ Success: $($Data.access_token.Substring(0, 20))..."
    }
}
catch {
    Write-Host "❌ Request failed: $_"
}
```

---

## Pro Tips

1. **Save responses to file** for comparison:
   ```powershell
   curl "$BASE_URL/recipes/?limit=10" | Out-File recipes.json
   ```

2. **Pretty print JSON**:
   ```powershell
   curl "$BASE_URL/recipes/?limit=3" | ConvertFrom-Json | ConvertTo-Json | Write-Host
   ```

3. **Count results**:
   ```powershell
   $(curl "$BASE_URL/recipes/" | ConvertFrom-Json).recipes.Count
   ```

4. **Filter results**:
   ```powershell
   $(curl "$BASE_URL/recipes/" | ConvertFrom-Json).recipes | Where-Object {$_.diet -eq "veg"}
   ```

---

**Ready to test? Start with the Health Checks, then follow the scenarios in order!**
