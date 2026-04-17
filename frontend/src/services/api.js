const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE;
  }

  getSavedCacheKey(token = this.getToken()) {
    return token ? `chefai_saved:${token}` : 'chefai_saved:anonymous';
  }

  getToken() {
    return localStorage.getItem('chefai_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken();

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw {
          status: response.status,
          message: data.detail || data.error || 'Something went wrong',
        };
      }

      return data;
    } catch (error) {
      if (error.status) throw error;
      throw { status: 0, message: 'Cannot connect to server. Is the backend running?' };
    }
  }

  // Auth
  async register(name, email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  }

  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data.access_token) {
      localStorage.setItem('chefai_token', data.access_token);
    }
    return data;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  async updateProfile(updates) {
    return this.request('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  logout() {
    const token = this.getToken();
    localStorage.removeItem('chefai_token');
    localStorage.removeItem('chefai_user');
    if (token) {
      localStorage.removeItem(this.getSavedCacheKey(token));
    }
    localStorage.removeItem('chefai_saved');
  }

  // Recipes
  async getRecipes(skip = 0, limit = 20, search = '', cuisine = '', diet = '', imageOnly = false) {
    const params = new URLSearchParams({ skip, limit });
    if (search) params.append('search', search);
    if (cuisine) params.append('cuisine', cuisine);
    if (diet) params.append('diet', diet);
    if (imageOnly) params.append('image_only', 'true');
    
    return this.request(`/recipes/?${params.toString()}`);
  }

  async getRecipe(id) {
    return this.request(`/recipes/${id}`);
  }

  // Recommendations
  async getRecommendations({ ingredients, timeLimit, cuisine, diet, servings, budgetLimit, healthGoal, wasteMode, pantryItems, userId }) {
    const body = { ingredients };
    if (userId) body.user_id = userId;
    if (timeLimit) body.time_limit = parseInt(timeLimit);
    if (cuisine) body.cuisine = cuisine;
    if (diet) body.diet = diet;
    if (servings) body.servings = parseInt(servings);
    if (budgetLimit) body.budget_limit = parseFloat(budgetLimit);
    if (healthGoal) body.health_goal = healthGoal;
    if (wasteMode) body.waste_mode = true;
    if (Array.isArray(pantryItems) && pantryItems.length > 0) body.pantry_items = pantryItems;

    return this.request('/recommend/', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getModelStats() {
    return this.request('/recommend/stats');
  }

  async submitFeedback({ recommendedRecipeId, accepted, context = '', reason = '' }) {
    return this.request('/feedback/', {
      method: 'POST',
      body: JSON.stringify({
        recommended_recipe_id: recommendedRecipeId,
        accepted,
        context,
        reason,
      }),
    });
  }

  async getPantry() {
    return this.request('/auth/pantry');
  }

  async updatePantry(items) {
    return this.request('/auth/pantry', {
      method: 'PUT',
      body: JSON.stringify({ items }),
    });
  }

  async getSavedRecipes() {
    return this.request('/saved/');
  }

  async getMyRecipes() {
    return this.request('/my-recipes/');
  }

  async markRecipeInterested(recipeId) {
    return this.request(`/my-recipes/${recipeId}/interested`, {
      method: 'POST',
    });
  }

  async startMyRecipe(recipeId) {
    return this.request(`/my-recipes/${recipeId}/start`, {
      method: 'POST',
    });
  }

  async updateMyRecipeProgress(recipeId, payload) {
    return this.request(`/my-recipes/${recipeId}/progress`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  async completeMyRecipe(recipeId) {
    return this.request(`/my-recipes/${recipeId}/complete`, {
      method: 'POST',
    });
  }

  getSavedRecipeIds() {
    try {
      return JSON.parse(localStorage.getItem(this.getSavedCacheKey()) || '[]');
    } catch {
      return [];
    }
  }

  setSavedRecipeIds(recipeIds) {
    localStorage.setItem(this.getSavedCacheKey(), JSON.stringify([...new Set(recipeIds)]));
  }

  clearSavedRecipeIds() {
    const token = this.getToken();
    if (token) {
      localStorage.removeItem(this.getSavedCacheKey(token));
    }
  }

  async saveRecipe(recipeId) {
    const response = await this.request(`/saved/${recipeId}`, {
      method: 'POST',
    });
    const saved = this.getSavedRecipeIds();
    if (!saved.includes(recipeId)) {
      this.setSavedRecipeIds([...saved, recipeId]);
    }
    return response;
  }

  async unsaveRecipe(recipeId) {
    const response = await this.request(`/saved/${recipeId}`, {
      method: 'DELETE',
    });
    const saved = this.getSavedRecipeIds().filter(id => id !== recipeId);
    this.setSavedRecipeIds(saved);
    return response;
  }

  isRecipeSaved(recipeId) {
    return this.getSavedRecipeIds().includes(recipeId);
  }
}

const api = new ApiService();
export default api;
