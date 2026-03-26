const API_BASE = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE;
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
    localStorage.removeItem('chefai_token');
    localStorage.removeItem('chefai_user');
  }

  // Recipes
  async getRecipes(skip = 0, limit = 20, search = '') {
    const url = `/recipes/?skip=${skip}&limit=${limit}${search ? `&search=${encodeURIComponent(search)}` : ''}`;
    return this.request(url);
  }

  async getRecipe(id) {
    return this.request(`/recipes/${id}`);
  }

  // Recommendations
  async getRecommendations({ ingredients, timeLimit, cuisine, diet, servings }) {
    const body = { ingredients };
    if (timeLimit) body.time_limit = parseInt(timeLimit);
    if (cuisine) body.cuisine = cuisine;
    if (diet) body.diet = diet;
    if (servings) body.servings = parseInt(servings);

    return this.request('/recommend/', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Saved Recipes (localStorage-based)
  getSavedRecipeIds() {
    try {
      return JSON.parse(localStorage.getItem('chefai_saved') || '[]');
    } catch {
      return [];
    }
  }

  saveRecipe(recipeId) {
    const saved = this.getSavedRecipeIds();
    if (!saved.includes(recipeId)) {
      saved.push(recipeId);
      localStorage.setItem('chefai_saved', JSON.stringify(saved));
    }
  }

  unsaveRecipe(recipeId) {
    const saved = this.getSavedRecipeIds().filter(id => id !== recipeId);
    localStorage.setItem('chefai_saved', JSON.stringify(saved));
  }

  isRecipeSaved(recipeId) {
    return this.getSavedRecipeIds().includes(recipeId);
  }
}

const api = new ApiService();
export default api;
