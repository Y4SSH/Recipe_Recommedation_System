import { useState, useEffect } from 'react';
import api from '../services/api';
import RecipeCard from '../components/recipe/RecipeCard';
import { Search, Filter, ChefHat } from 'lucide-react';
import './Explore.css';

const CUISINE_CARDS = [
  { name: 'Indian', emoji: '🇮🇳' },
  { name: 'South Indian Recipes', emoji: '🥘', label: 'South Indian' },
  { name: 'North Indian Recipes', emoji: '🍛', label: 'North Indian' },
  { name: 'Chinese', emoji: '🥡' },
  { name: 'Continental', emoji: '🍝' },
  { name: 'Bengali Recipes', emoji: '🐟', label: 'Bengali' },
  { name: 'Punjabi', emoji: '🧈' },
  { name: 'Kerala Recipes', emoji: '🌴', label: 'Kerala' },
];

export default function Explore() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 20;

  const fetchRecipes = async (skip = 0, append = false) => {
    try {
      setLoading(true);
      const data = await api.getRecipes(skip, LIMIT);
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
    fetchRecipes(0);
  }, []);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchRecipes(nextPage * LIMIT, true);
  };

  const filteredRecipes = recipes.filter(r => {
    const matchesSearch = !searchQuery ||
      r.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.cuisine?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCuisine = !selectedCuisine ||
      r.cuisine?.toLowerCase().includes(selectedCuisine.toLowerCase());
    return matchesSearch && matchesCuisine;
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
          <h3><Filter size={16} /> Filter by Cuisine</h3>
          <div className="cuisine-chips">
            <button
              className={`cuisine-chip ${!selectedCuisine ? 'cuisine-chip-active' : ''}`}
              onClick={() => setSelectedCuisine('')}
            >
              🌍 All
            </button>
            {CUISINE_CARDS.map(c => (
              <button
                key={c.name}
                className={`cuisine-chip ${selectedCuisine === c.name ? 'cuisine-chip-active' : ''}`}
                onClick={() => setSelectedCuisine(selectedCuisine === c.name ? '' : c.name)}
              >
                {c.emoji} {c.label || c.name}
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
          ) : filteredRecipes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><ChefHat size={32} /></div>
              <h3>No recipes found</h3>
              <p>Try a different search term or clear the cuisine filter.</p>
            </div>
          ) : (
            <>
              <p className="explore-count">{filteredRecipes.length} recipe{filteredRecipes.length !== 1 ? 's' : ''}</p>
              <div className="recipe-grid">
                {filteredRecipes.map((recipe, i) => (
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
