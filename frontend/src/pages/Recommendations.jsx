import { useState, useEffect, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../services/api';
import RecipeCard from '../components/recipe/RecipeCard';
import { Sparkles, ArrowLeft, SlidersHorizontal, ChefHat } from 'lucide-react';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import './Recommendations.css';

export default function Recommendations() {
  const [searchParams] = useSearchParams();
  const toast = useToast();
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedbackMap, setFeedbackMap] = useState({});
  const [factIndex, setFactIndex] = useState(0);

  const ingredients = searchParams.get('ingredients')?.split(',').filter(Boolean) || [];
  const timeLimit = searchParams.get('timeLimit');
  const cuisine = searchParams.get('cuisine');
  const diet = searchParams.get('diet');
  const servings = searchParams.get('servings');
  const budget = searchParams.get('budget');
  const healthGoal = searchParams.get('healthGoal');
  const wasteMode = searchParams.get('wasteMode') === '1';
  const pantry = searchParams.get('pantry');
  const broadMatchNote = recommendations.find((rec) =>
    (rec.explanation || []).some((line) => line.includes('search was broadened'))
  );

  const foodFacts = useMemo(() => [
    'Tomatoes are technically fruits, but they are used as vegetables in cooking.',
    'Turmeric has been used in Indian kitchens for centuries as both spice and color.',
    'Rice is the staple food for more than half the world’s population.',
    'Chili peppers release a compound called capsaicin, which creates the spicy heat.',
  ], []);

  const dietLabel = diet === 'veg' ? 'veg' : diet === 'non-veg' ? 'non-veg' : diet;

  let pantryItems = [];
  try {
    pantryItems = pantry ? JSON.parse(decodeURIComponent(pantry)) : [];
  } catch {
    pantryItems = [];
  }

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
          ingredients,
          timeLimit,
          cuisine,
          diet,
          servings,
          budgetLimit: budget,
          healthGoal,
          wasteMode,
          pantryItems,
          userId: user?.id,
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

  useEffect(() => {
    if (!loading) return undefined;

    const timer = window.setInterval(() => {
      setFactIndex((value) => (value + 1) % foodFacts.length);
    }, 4200);

    return () => window.clearInterval(timer);
  }, [loading, foodFacts.length]);

  const handleFeedback = async (recipeId, accepted) => {
    try {
      await api.submitFeedback({
        recommendedRecipeId: recipeId,
        accepted,
        context: JSON.stringify({ ingredients, timeLimit, cuisine, diet, servings, budget, healthGoal, wasteMode }),
        reason: accepted ? 'Helpful recommendation' : 'Not suitable for my current need',
      });

      setFeedbackMap((prev) => ({ ...prev, [recipeId]: accepted ? 'helpful' : 'not_helpful' }));
      toast.success(accepted ? 'Marked as useful. Model will adapt.' : 'Thanks! We will improve future results.');
    } catch (err) {
      toast.error(err.message || 'Unable to submit feedback right now');
    }
  };

  const handleInterested = async (recipeId) => {
    try {
      await api.markRecipeInterested(recipeId);
      toast.success('Added to My Recipes');
    } catch (err) {
      toast.error(err.message || 'Unable to add recipe right now');
    }
  };

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
                {dietLabel && <span className="tag tag-neutral">🥗 {dietLabel}</span>}
                {timeLimit && <span className="tag tag-neutral">⏱️ ≤{timeLimit} min</span>}
                {budget && <span className="tag tag-neutral">💸 ${budget} budget</span>}
                {healthGoal && <span className="tag tag-neutral">🧠 {healthGoal}</span>}
                {wasteMode && <span className="tag tag-neutral">♻️ Zero-Waste</span>}
              </div>
            )}
          </div>
        )}

        {broadMatchNote && !loading && !error && (
          <div className="empty-state" style={{ marginBottom: 24, textAlign: 'left' }}>
            <div className="empty-state-icon"><ChefHat size={32} /></div>
            <h3>Broadened search</h3>
            <p>We did not find a direct overlap for your exact ingredients, so the closest recipes are shown instead.</p>
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
              <div className="rec-loading-fact" aria-live="polite">
                <span>Food fact:</span>
                <p>{foodFacts[factIndex]}</p>
              </div>
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
                <RecipeCard
                  key={rec.id}
                  recommendation={rec}
                  recipe={rec.recipe}
                  index={i}
                  compact
                  showInterestedAction
                  onInterested={handleInterested}
                  showFeedback
                  feedbackState={feedbackMap[rec.recipe?.id || rec.id]}
                  onFeedback={handleFeedback}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
