import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import RecipeCard from '../components/recipe/RecipeCard';
import { Bookmark, ChefHat, Trash2, Folder, BookOpen } from 'lucide-react';
import './SavedRecipes.css';

export default function SavedRecipes() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeCollection, setActiveCollection] = useState('All');

  const collections = ['All', 'Weeknight dinners', 'Indian', 'Quick meals'];

  useEffect(() => {
    const fetchSaved = async () => {
      setLoading(true);
      try {
        const results = await api.getSavedRecipes();
        setRecipes(results);
      } catch {
        setRecipes([]);
      } finally {
        setLoading(false);
      }
    };
    fetchSaved();
  }, [refreshKey]);

  const handleClearAll = async () => {
    setLoading(true);
    try {
      await Promise.all(recipes.map(recipe => api.unsaveRecipe(recipe.id).catch(() => null)));
      setRecipes([]);
    } finally {
      setLoading(false);
    }
    setRefreshKey(k => k + 1);
  };

  return (
    <div className="page">
      <div className="container">
        <div className="page-header animate-fade-in-up">
          <h1>
            <BookOpen size={28} style={{ marginRight: 12 }} /> 
            Personal Cookbook
          </h1>
          <p>Your curated collection of favorite recipes</p>
        </div>

        <div className="collections-bar animate-fade-in-up stagger-1">
          <div className="collections-scroll">
            {collections.map(c => (
              <button 
                key={c}
                className={`collection-tab ${activeCollection === c ? 'collection-tab-active' : ''}`}
                onClick={() => setActiveCollection(c)}
              >
                <Folder size={14} /> {c}
              </button>
            ))}
          </div>
        </div>

        {recipes.length > 0 && (
          <div className="saved-actions animate-fade-in-up stagger-2">
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
              <div className="empty-state-illustration">
                🍽️
              </div>
              <h3>Your cookbook is empty</h3>
              <p>Save recipes to build your personal collection of go-to meals.</p>
              <Link to="/explore" className="btn btn-primary" style={{ marginTop: 24 }}>
                <ChefHat size={18} /> Discover Recipes
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
