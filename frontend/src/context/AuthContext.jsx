import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [savedRecipeIds, setSavedRecipeIds] = useState([]);
  const [savedRecipesLoading, setSavedRecipesLoading] = useState(false);

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('chefai_token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const userData = await api.getMe();
      setUser(userData);
      setIsAuthenticated(true);
    } catch {
      localStorage.removeItem('chefai_token');
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshSavedRecipes = useCallback(async () => {
    if (!isAuthenticated || !user?.id) {
      setSavedRecipeIds([]);
      return [];
    }

    setSavedRecipesLoading(true);
    try {
      const savedRecipes = await api.getSavedRecipes();
      const ids = savedRecipes.map(recipe => recipe.id);
      setSavedRecipeIds(ids);
      api.setSavedRecipeIds(ids);
      return ids;
    } catch {
      setSavedRecipeIds([]);
      api.setSavedRecipeIds([]);
      return [];
    } finally {
      setSavedRecipesLoading(false);
    }
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      refreshSavedRecipes();
      return;
    }
    setSavedRecipeIds([]);
    setSavedRecipesLoading(false);
  }, [isAuthenticated, user?.id, refreshSavedRecipes]);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    setUser(data.user);
    setIsAuthenticated(true);
    return data;
  };

  const register = async (name, email, password) => {
    const data = await api.register(name, email, password);
    return data;
  };

  const updateProfile = async (updates) => {
    const data = await api.updateProfile(updates);
    setUser(data);
    return data;
  };

  const logout = () => {
    api.clearSavedRecipeIds();
    api.logout();
    setUser(null);
    setIsAuthenticated(false);
    setSavedRecipeIds([]);
  };

  const saveRecipe = async (recipeId) => {
    await api.saveRecipe(recipeId);
    setSavedRecipeIds(prev => (prev.includes(recipeId) ? prev : [...prev, recipeId]));
  };

  const unsaveRecipe = async (recipeId) => {
    await api.unsaveRecipe(recipeId);
    setSavedRecipeIds(prev => prev.filter(id => id !== recipeId));
  };

  const isRecipeSaved = useCallback((recipeId) => {
    return savedRecipeIds.includes(recipeId);
  }, [savedRecipeIds]);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      isAuthenticated,
      savedRecipeIds,
      savedRecipesLoading,
      refreshSavedRecipes,
      isRecipeSaved,
      saveRecipe,
      unsaveRecipe,
      login,
      register,
      updateProfile,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
