import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../services/api';
import RecipeCard from '../components/recipe/RecipeCard';
import { Sparkles, ArrowLeft, SlidersHorizontal, ChefHat } from 'lucide-react';
import './Recommendations.css';

export default function Recommendations() {
  const [searchParams] = useSearchParams();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const ingredients = searchParams.get('ingredients')?.split(',').filter(Boolean) || [];
  const timeLimit = searchParams.get('timeLimit');
  const cuisine = searchParams.get('cuisine');
  const diet = searchParams.get('diet');
  const servings = searchParams.get('servings');

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (ingredients.length === 0) {
        setError('No ingredients provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await api.getRecommendations({
          ingredients, timeLimit, cuisine, diet, servings
        });
        setRecommendations(data.recommendations || []);
      } catch (err) {
        setError(err.message || 'Failed to get recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [searchParams.toString()]);

  return (
    <div className="page">
      <div className="container">
        <div className="rec-header animate-fade-in-up">
          <Link to="/dashboard" className="btn btn-ghost">
            <ArrowLeft size={18} />
            Back
          </Link>
          <div className="rec-header-content">
            <h1 className="page-title">
              <Sparkles size={28} className="text-gradient-icon" />
              AI Recommendations
            </h1>
            <p className="rec-subtitle">
              {loading ? 'Finding recipes...' :
                `Found ${recommendations.length} recipe${recommendations.length !== 1 ? 's' : ''} for your ingredients`}
            </p>
          </div>
        </div>

        {ingredients.length > 0 && (
          <div className="rec-filters-bar animate-fade-in-up stagger-1">
            <div className="rec-ingredients-list">
              <SlidersHorizontal size={16} />
              <span className="rec-filter-label">Your ingredients:</span>
              {ingredients.map(ing => (
                <span key={ing} className="tag tag-primary">{ing}</span>
              ))}
            </div>
            {(cuisine || diet || timeLimit) && (
              <div className="rec-active-filters">
                {cuisine && <span className="tag tag-neutral">🌍 {cuisine}</span>}
                {diet && <span className="tag tag-neutral">🥗 {diet}</span>}
                {timeLimit && <span className="tag tag-neutral">⏱️ ≤{timeLimit} min</span>}
              </div>
            )}
          </div>
        )}

        <div className="rec-content">
          {loading ? (
            <div className="loading-container">
              <div className="rec-loading-animation">
                <div className="rec-loading-plate">🍽️</div>
                <div className="loading-spinner" />
              </div>
              <p className="loading-text">Our AI chef is finding the perfect recipes for you...</p>
            </div>
          ) : error ? (
            <div className="empty-state">
              <div className="empty-state-icon"><ChefHat size={32} /></div>
              <h3>Oops!</h3>
              <p>{error}</p>
              <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 16 }}>Go to Dashboard</Link>
            </div>
          ) : recommendations.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><ChefHat size={32} /></div>
              <h3>No recipes found</h3>
              <p>Try adding different ingredients or removing some filters.</p>
              <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 16 }}>Try Again</Link>
            </div>
          ) : (
            <div className="recipe-grid animate-fade-in">
              {recommendations.map((rec, i) => (
                <RecipeCard key={rec.id} recommendation={rec} recipe={rec.recipe} index={i} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
