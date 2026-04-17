import { useState, useEffect } from 'react';
import api from '../services/api';
import RecipeCard from '../components/recipe/RecipeCard';
import { Search, Filter, ChefHat, Globe } from 'lucide-react';
import './Explore.css';

const CUISINE_CARDS = [
  { value: 'indian', icon: <Globe size={14} />, label: 'Indian' },
];

export default function Explore() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [selectedDiet, setSelectedDiet] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 20;

  const fetchRecipes = async (skip = 0, append = false, query = '', cuisine = '', diet = '') => {
    try {
      setLoading(true);
      // Load the full recipe list; the UI will still prioritize recipes with usable images.
      const data = await api.getRecipes(skip, LIMIT, query, cuisine, diet, false);
      if (append) {
        setRecipes(prev => [...prev, ...data]);
      } else {
        setRecipes(data);
      }
      setHasMore(data.length === LIMIT);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setPage(0);
      fetchRecipes(0, false, searchQuery, selectedCuisine, selectedDiet);
    }, 400);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, selectedCuisine, selectedDiet]);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchRecipes(nextPage * LIMIT, true, searchQuery, selectedCuisine, selectedDiet);
  };

  const hasUsableImage = (recipe) => {
    const url = (recipe?.image_url || '').trim().toLowerCase();
    if (!url) return false;
    // Keep obviously broken legacy hosts behind usable/local images.
    if (url.includes('archanaskitchen')) return false;
    return true;
  };

  // The backend already filters it for us now! 
  // We can just render "recipes" directly, but we keep this harmless local filter just in case 
  // there's a tiny sync delay or they typed extremely fast.
  const filteredRecipes = recipes.filter(r => {
    const matchesSearch = !searchQuery ||
      r.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.cuisine?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCuisine = !selectedCuisine ||
      r.cuisine?.toLowerCase().includes(selectedCuisine.toLowerCase());
    return matchesSearch && matchesCuisine;
  });

  const prioritizedRecipes = [...filteredRecipes].sort((a, b) => {
    const aHasImage = hasUsableImage(a) ? 1 : 0;
    const bHasImage = hasUsableImage(b) ? 1 : 0;
    return bHasImage - aHasImage;
  });

  return (
    <div className="page">
      <div className="container">
        <div className="page-header animate-fade-in-up">
          <h1>Explore Recipes</h1>
          <p>Discover amazing dishes from around the world</p>
        </div>

        <div className="explore-search animate-fade-in-up stagger-1">
          <div className="explore-search-box">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search recipes by name or cuisine..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="explore-search-input"
            />
          </div>
        </div>

        <div className="explore-cuisines animate-fade-in-up stagger-2">
          <div className="cuisine-chips">
            <button
              className={`cuisine-chip ${!selectedDiet ? 'cuisine-chip-active' : ''}`}
              onClick={() => setSelectedDiet('')}
            >
              All Diets
            </button>
            <button
              className={`cuisine-chip ${selectedDiet === 'veg' ? 'cuisine-chip-active' : ''}`}
              onClick={() => setSelectedDiet(selectedDiet === 'veg' ? '' : 'veg')}
              style={selectedDiet === 'veg' ? {background: '#10b981', color: '#fff', borderColor: '#10b981'} : {}}
            >
              <span className="veg-dot" style={{ display: 'inline-block', width: 8, height: 8, background: selectedDiet === 'veg' ? '#fff' : '#10b981', borderRadius: '50%', marginRight: 6 }}></span>
              Veg
            </button>
            <button
              className={`cuisine-chip ${selectedDiet === 'non-veg' ? 'cuisine-chip-active' : ''}`}
              onClick={() => setSelectedDiet(selectedDiet === 'non-veg' ? '' : 'non-veg')}
              style={selectedDiet === 'non-veg' ? {background: '#ef4444', color: '#fff', borderColor: '#ef4444'} : {}}
            >
              <span className="non-veg-dot" style={{ display: 'inline-block', width: 8, height: 8, background: selectedDiet === 'non-veg' ? '#fff' : '#ef4444', borderRadius: '50%', marginRight: 6 }}></span>
              Non-Veg
            </button>
          </div>

          <h3 style={{ marginTop: 'var(--space-md)' }}><Filter size={16} /> Filter by Cuisine</h3>
          <div className="cuisine-chips">
            <button
              className={`cuisine-chip ${!selectedCuisine ? 'cuisine-chip-active' : ''}`}
              onClick={() => setSelectedCuisine('')}
            >
              <span className="cuisine-chip-icon"><Globe size={14} /></span>
              Any (Indian dataset)
            </button>
            {CUISINE_CARDS.map(c => (
              <button
                key={c.value}
                className={`cuisine-chip ${selectedCuisine === c.value ? 'cuisine-chip-active' : ''}`}
                onClick={() => setSelectedCuisine(selectedCuisine === c.value ? '' : c.value)}
              >
                <span className="cuisine-chip-icon">{c.icon}</span>
                {c.label}
              </button>
            ))}
          </div>
        </div>

        <div className="explore-content">
          {loading && recipes.length === 0 ? (
            <div className="loading-container">
              <div className="loading-spinner" />
              <p className="loading-text">Loading recipes...</p>
            </div>
          ) : prioritizedRecipes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><ChefHat size={32} /></div>
              <h3>No recipes found</h3>
              <p>Try a different search term or clear the cuisine filter.</p>
            </div>
          ) : (
            <>
              <p className="explore-count">{prioritizedRecipes.length} recipe{prioritizedRecipes.length !== 1 ? 's' : ''}</p>
              <div className="recipe-grid">
                {prioritizedRecipes.map((recipe, i) => (
                  <RecipeCard key={recipe.id} recipe={recipe} index={i} />
                ))}
              </div>
              {hasMore && !searchQuery && !selectedCuisine && (
                <div className="explore-load-more">
                  <button className="btn btn-secondary btn-lg" onClick={loadMore} disabled={loading}>
                    {loading ? 'Loading...' : 'Load More Recipes'}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
