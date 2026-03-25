import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import RecipeCard from '../components/recipe/RecipeCard';
import { Bookmark, ChefHat, Trash2 } from 'lucide-react';
import './SavedRecipes.css';

export default function SavedRecipes() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const fetchSaved = async () => {
      setLoading(true);
      const savedIds = api.getSavedRecipeIds();
      if (savedIds.length === 0) {
        setRecipes([]);
        setLoading(false);
        return;
      }

      try {
        const results = await Promise.all(
          savedIds.map(id => api.getRecipe(id).catch(() => null))
        );
        setRecipes(results.filter(Boolean));
      } catch {
        setRecipes([]);
      } finally {
        setLoading(false);
      }
    };
    fetchSaved();
  }, [refreshKey]);

  const handleClearAll = () => {
    localStorage.removeItem('chefai_saved');
    setRefreshKey(k => k + 1);
  };

  return (
    <div className="page">
      <div className="container">
        <div className="page-header animate-fade-in-up">
          <h1>
            <Bookmark size={28} /> Saved Recipes
          </h1>
          <p>Your personal cookbook of bookmarked recipes</p>
        </div>

        {recipes.length > 0 && (
          <div className="saved-actions animate-fade-in-up">
            <span className="saved-count">{recipes.length} saved recipe{recipes.length !== 1 ? 's' : ''}</span>
            <button className="btn btn-danger btn-sm" onClick={handleClearAll}>
              <Trash2 size={14} /> Clear All
            </button>
          </div>
        )}

        <div className="saved-content">
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner" />
              <p className="loading-text">Loading saved recipes...</p>
            </div>
          ) : recipes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><Bookmark size={32} /></div>
              <h3>No saved recipes yet</h3>
              <p>Start exploring and save your favorite recipes to access them quickly later.</p>
              <Link to="/explore" className="btn btn-primary" style={{ marginTop: 16 }}>
                Explore Recipes
              </Link>
            </div>
          ) : (
            <div className="recipe-grid animate-fade-in">
              {recipes.map((recipe, i) => (
                <RecipeCard
                  key={recipe.id}
                  recipe={recipe}
                  index={i}
                  onSaveToggle={() => setRefreshKey(k => k + 1)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
