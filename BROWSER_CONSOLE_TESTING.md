# Browser Console Testing Guide

Use this guide to test the frontend API integration directly from your browser's developer console.

---

## Opening DevTools

- **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I`
- **Firefox**: Press `F12` or `Ctrl+Shift+I`
- Click the **Console** tab

---

## Getting Started

### Check if Auth Token Exists
```javascript
const token = localStorage.getItem('authToken');
console.log('Auth Token:', token ? token.substring(0, 30) + '...' : 'NOT FOUND');
console.log('Token length:', token?.length);
```

### Get Current User
```javascript
const user = JSON.parse(localStorage.getItem('user') || '{}');
console.log('Current User:', user);
```

### API Base URL
```javascript
const API_BASE = 'http://localhost:8000';
console.log('API Base:', API_BASE);
```

---

## Frontend Navigation Testing

### Go to Dashboard
```javascript
window.location.href = '/dashboard';
```

### Go to Explore
```javascript
window.location.href = '/explore';
```

### Go to Recommendations
```javascript
window.location.href = '/recommend';
```

### Go to Saved Recipes
```javascript
window.location.href = '/saved';
```

### Go to Recipe Detail (Replace recipe_id)
```javascript
window.location.href = '/recipe/aloo-gobi-id-here';
```

---

## API Integration Testing

### Helper Function: Make API Calls
```javascript
async function apiCall(method, endpoint, body = null) {
  const token = localStorage.getItem('authToken');
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const options = {
    method,
    headers
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(`http://localhost:8000${endpoint}`, options);
    const data = await response.json();
    console.log(`${method} ${endpoint}:`, data);
    return data;
  } catch (error) {
    console.error(`Error calling ${endpoint}:`, error);
  }
}

// Make this available globally
window.apiCall = apiCall;
```

**Then use it like:**
```javascript
await apiCall('GET', '/auth/me');
```

---

## Authentication Testing

### Test Login Endpoint
```javascript
async function testLogin() {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'testuser@example.com',
      password: 'securePassword123!'
    })
  });
  
  const data = await response.json();
  console.log('Login Response:', data);
  
  // Save token
  if (data.access_token) {
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    console.log('✅ Token saved to localStorage');
  }
  
  return data;
}

await testLogin();
```

### Test Get Profile
```javascript
async function getProfile() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  console.log('Profile:', data);
  return data;
}

await getProfile();
```

---

## Recipe Testing

### List All Recipes
```javascript
async function listRecipes(limit = 10) {
  const response = await fetch(`http://localhost:8000/recipes/?limit=${limit}`);
  const data = await response.json();
  console.log(`Found ${data.total} recipes, showing ${data.recipes.length}`);
  console.table(data.recipes.map(r => ({
    id: r.id,
    name: r.name,
    cuisine: r.cuisine,
    diet: r.diet,
    variant_type: r.variant_type
  })));
  return data.recipes;
}

const recipes = await listRecipes(10);
```

### Get Single Recipe
```javascript
async function getRecipe(recipeId) {
  const response = await fetch(`http://localhost:8000/recipes/${recipeId}`);
  const data = await response.json();
  console.log('Recipe Details:', data);
  return data;
}

// Use a recipe ID from previous list
await getRecipe('aloo-gobi');
```

### Filter by Cuisine
```javascript
async function filterByCuisine(cuisine = 'indian', limit = 10) {
  const response = await fetch(`http://localhost:8000/recipes/?cuisine=${cuisine}&limit=${limit}`);
  const data = await response.json();
  console.log(`Found ${data.recipes.length} ${cuisine} recipes`);
  console.table(data.recipes.map(r => ({name: r.name, diet: r.diet})));
  return data.recipes;
}

await filterByCuisine('indian', 5);
```

### Filter by Diet
```javascript
async function filterByDiet(diet = 'veg', limit = 10) {
  const response = await fetch(`http://localhost:8000/recipes/?diet=${diet}&limit=${limit}`);
  const data = await response.json();
  console.log(`Found ${data.recipes.length} ${diet} recipes`);
  console.table(data.recipes.map(r => ({name: r.name, cuisine: r.cuisine})));
  return data.recipes;
}

await filterByDiet('veg', 5);
```

---

## Recommendation Testing

### Get Recommendations
```javascript
async function getRecommendations(ingredients) {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/recommend/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ ingredients })
  });
  
  const data = await response.json();
  console.log(`Got ${data.recommendations.length} recommendations`);
  console.table(data.recommendations.map(r => ({
    name: r.name,
    score: (r.score * 100).toFixed(1) + '%',
    explanation: r.explanation.substring(0, 50) + '...'
  })));
  return data.recommendations;
}

const recs = await getRecommendations(['potatoes', 'onions', 'tomatoes']);
```

### Test Zero-Overlap Fallback
```javascript
async function testFallback() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/recommend/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ 
      ingredients: ['xyz_fake_ingredient_123', 'qwerty_notreal_456']
    })
  });
  
  const data = await response.json();
  console.log('🔍 Testing Fallback:');
  console.log(`Got ${data.recommendations.length} recommendations despite zero overlap`);
  
  if (data.recommendations.length > 0) {
    const firstExplanation = data.recommendations[0].explanation;
    console.log('✅ FALLBACK WORKING - Recommendation:', data.recommendations[0].name);
    console.log('Explanation:', firstExplanation);
    
    if (firstExplanation.toLowerCase().includes('broadened')) {
      console.log('✅ Explanation mentions "broadened search"');
    }
  }
  
  return data.recommendations;
}

await testFallback();
```

### Get Recommendation Stats
```javascript
async function getStats() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/recommend/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  console.log('Recommendation Engine Stats:');
  console.table(data);
  return data;
}

await getStats();
```

---

## Saved Recipes Testing

### Get Saved Recipes
```javascript
async function getSavedRecipes() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/saved/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  console.log(`Total saved recipes: ${data.total}`);
  console.table(data.saved_recipes.map(r => ({
    name: r.name,
    cuisine: r.cuisine,
    diet: r.diet
  })));
  return data.saved_recipes;
}

const saved = await getSavedRecipes();
```

### Save a Recipe
```javascript
async function saveRecipe(recipeId) {
  const token = localStorage.getItem('authToken');
  const response = await fetch(`http://localhost:8000/saved/${recipeId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  console.log('✅ Recipe saved:', data);
  return data;
}

// Use a recipe ID
await saveRecipe('aloo-gobi');
```

### Delete Saved Recipe
```javascript
async function deleteSavedRecipe(recipeId) {
  const token = localStorage.getItem('authToken');
  const response = await fetch(`http://localhost:8000/saved/${recipeId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('✅ Recipe deleted');
  return response.ok;
}

await deleteSavedRecipe('aloo-gobi');
```

---

## Rating Testing

### Rate a Recipe
```javascript
async function rateRecipe(recipeId, score) {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/ratings/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ recipe_id: recipeId, score })
  });
  const data = await response.json();
  console.log(`✅ Rated ${recipeId}: ${score}/5`, data);
  return data;
}

await rateRecipe('aloo-gobi', 4);
```

### Get My Ratings
```javascript
async function getMyRatings() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/ratings/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  console.log(`Total ratings: ${data.ratings?.length || 0}`);
  console.table(data.ratings);
  return data;
}

await getMyRatings();
```

---

## Feedback Testing

### Submit Feedback
```javascript
async function submitFeedback(recipeId, accepted = true, notes = '') {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/feedback/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      recommended_recipe_id: recipeId,
      accepted,
      notes
    })
  });
  const data = await response.json();
  console.log(`✅ Feedback submitted (${accepted ? 'accepted' : 'rejected'})`);
  return data;
}

await submitFeedback('aloo-gobi', true, 'Loved this recipe!');
```

### Get My Feedback
```javascript
async function getMyFeedback() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('http://localhost:8000/feedback/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  console.log(`Total feedback entries: ${data.feedback?.length || 0}`);
  console.table(data.feedback);
  return data;
}

await getMyFeedback();
```

---

## UI Element Testing

### Check if Cuisine Filter Shows Only 2 Options
```javascript
// On Dashboard or Explore page
const cuisineOptions = document.querySelectorAll('[data-testid="cuisine-option"]');
console.log(`Found ${cuisineOptions.length} cuisine options`);

if (cuisineOptions.length === 2) {
  console.log('✅ CORRECT: Exactly 2 cuisine options');
} else {
  console.log(`❌ WRONG: Expected 2, found ${cuisineOptions.length}`);
}

// List them
cuisineOptions.forEach((opt, i) => {
  console.log(`${i + 1}. ${opt.textContent}`);
});
```

### Check if Metadata Tags Visible
```javascript
// On Recipe Detail page
const metadataTags = document.querySelectorAll('[data-testid="metadata-tag"]');
console.log(`Found ${metadataTags.length} metadata tags`);

const metadata = {};
metadataTags.forEach(tag => {
  const key = tag.getAttribute('data-key');
  const value = tag.textContent;
  metadata[key] = value;
  console.log(`  ${key}: ${value}`);
});

if (metadata.variant_type && metadata.cooking_method && metadata.protein_type) {
  console.log('✅ All expected metadata visible');
} else {
  console.log('❌ Missing some metadata fields');
}
```

### Check for Fallback Notice
```javascript
// On Recommendations page after zero-overlap search
const fallbackNotice = document.querySelector('[data-testid="fallback-notice"]');

if (fallbackNotice) {
  console.log('✅ Fallback notice found:');
  console.log(fallbackNotice.textContent);
} else {
  console.log('❌ Fallback notice not found');
}
```

### Verify Auth Token in LocalStorage
```javascript
const token = localStorage.getItem('authToken');
const user = localStorage.getItem('user');

console.log('Token exists:', !!token);
console.log('User exists:', !!user);
console.log('Token length:', token?.length);
console.log('User data:', user ? JSON.parse(user) : null);
```

---

## Performance Testing

### Measure API Response Times
```javascript
async function measureResponseTime(endpoint, options = {}) {
  const start = performance.now();
  
  const response = await fetch(endpoint, options);
  const data = await response.json();
  
  const end = performance.now();
  const duration = end - start;
  
  console.log(`${endpoint}: ${duration.toFixed(2)}ms`);
  return { duration, data };
}

// Test multiple endpoints
const results = [];
results.push(await measureResponseTime('http://localhost:8000/recipes/?limit=10'));
results.push(await measureResponseTime('http://localhost:8000/recipes/?diet=veg&limit=5'));

console.table(results.map((r, i) => ({
  '#': i + 1,
  'Time (ms)': r.duration.toFixed(2)
})));
```

### Test Recommendation Latency (Cold vs Warm)
```javascript
async function testRecommendationLatency() {
  const token = localStorage.getItem('authToken');
  
  for (let i = 1; i <= 3; i++) {
    const start = performance.now();
    
    await fetch('http://localhost:8000/recommend/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ ingredients: ['potato', 'onion'] })
    }).then(r => r.json());
    
    const end = performance.now();
    const duration = end - start;
    
    console.log(`Request ${i}: ${duration.toFixed(2)}ms`);
  }
}

await testRecommendationLatency();
```

---

## Helper Commands

### Copy Token to Clipboard
```javascript
const token = localStorage.getItem('authToken');
navigator.clipboard.writeText(token);
console.log('✅ Token copied to clipboard');
```

### Clear All Cached Data
```javascript
localStorage.clear();
sessionStorage.clear();
console.log('✅ All storage cleared');
```

### Export All Test Results
```javascript
const results = {
  timestamp: new Date().toISOString(),
  userAgent: navigator.userAgent,
  localStorage: { ...localStorage },
  tests: {}
};

console.log(JSON.stringify(results, null, 2));
```

---

## Quick Test Suite

**Copy-paste this entire block to run a quick test:**

```javascript
// Quick Test Suite
(async () => {
  console.log('🧪 Starting Quick Test Suite...\n');
  
  try {
    // 1. Check health
    const health = await fetch('http://localhost:8000/health').then(r => r.json());
    console.log('✅ Health:', health.status);
    
    // 2. Get recipes
    const recipes = await fetch('http://localhost:8000/recipes/?limit=3').then(r => r.json());
    console.log(`✅ Recipes: ${recipes.total} total, showing 3`);
    
    // 3. Filter by diet
    const veg = await fetch('http://localhost:8000/recipes/?diet=veg&limit=3').then(r => r.json());
    console.log(`✅ Veg recipes: ${veg.recipes.length} results`);
    
    // 4. Check auth
    const token = localStorage.getItem('authToken');
    console.log(`✅ Auth: ${token ? 'Authenticated' : 'Not authenticated'}`);
    
    if (token) {
      const profile = await fetch('http://localhost:8000/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(r => r.json());
      console.log(`✅ User: ${profile.email}`);
    }
    
    console.log('\n✅ All quick tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
})();
```

---

**Ready to test? Open DevTools Console and start with "Getting Started" section!**
