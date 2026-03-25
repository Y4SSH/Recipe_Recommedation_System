import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { useToast } from '../context/ToastContext';
import {
  ArrowLeft, Clock, Users, ChefHat, Globe, Bookmark, BookmarkCheck,
  Share2, CheckCircle, Star
} from 'lucide-react';
import './RecipeDetail.css';

export default function RecipeDetailPage() {
  const { id } = useParams();
  const toast = useToast();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [checkedSteps, setCheckedSteps] = useState({});
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const data = await api.getRecipe(id);
        setRecipe(data);
        setSaved(api.isRecipeSaved(id));
      } catch {
        toast.error('Recipe not found');
      } finally {
        setLoading(false);
      }
    };
    fetchRecipe();
  }, [id]);

  const toggleSave = () => {
    if (saved) {
      api.unsaveRecipe(id);
      setSaved(false);
      toast.info('Recipe removed from bookmarks');
    } else {
      api.saveRecipe(id);
      setSaved(true);
      toast.success('Recipe saved! 🔖');
    }
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    } catch {
      toast.info('Could not copy link');
    }
  };

  const toggleStep = (i) => {
    setCheckedSteps(prev => ({ ...prev, [i]: !prev[i] }));
  };

  const parseIngredients = (recipe) => {
    if (!recipe.ingredients) return [];
    try {
      const parsed = JSON.parse(recipe.ingredients);
      if (Array.isArray(parsed)) return parsed.map(i => typeof i === 'string' ? i : i.name || String(i));
    } catch {}
    return recipe.ingredients.split(',').map(s => s.trim()).filter(Boolean);
  };

  const parseSteps = (recipe) => {
    if (!recipe.steps) return [];
    try {
      const parsed = JSON.parse(recipe.steps);
      if (Array.isArray(parsed)) return parsed.map(s => typeof s === 'string' ? s : String(s));
    } catch {}
    return recipe.steps.split(/\.\s+/).map(s => s.trim()).filter(s => s.length > 10);
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-container">
          <div className="loading-spinner" />
          <p className="loading-text">Loading recipe...</p>
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="page">
        <div className="container">
          <div className="empty-state">
            <div className="empty-state-icon"><ChefHat size={32} /></div>
            <h3>Recipe not found</h3>
            <Link to="/explore" className="btn btn-primary" style={{ marginTop: 16 }}>Browse Recipes</Link>
          </div>
        </div>
      </div>
    );
  }

  const ingredients = parseIngredients(recipe);
  const steps = parseSteps(recipe);
  const fallbackBg = 'linear-gradient(135deg, #FF6B35 0%, #C41E3A 50%, #7B2D8E 100%)';

  return (
    <div className="page recipe-detail-page">
      <div className="rd-hero">
        {recipe.image_url ? (
          <img src={recipe.image_url} alt={recipe.title} className="rd-hero-img" onError={(e) => {
            e.target.style.display = 'none';
            e.target.parentElement.style.background = fallbackBg;
          }} />
        ) : (
          <div className="rd-hero-placeholder" style={{ background: fallbackBg }}>
            <ChefHat size={64} />
          </div>
        )}
        <div className="rd-hero-overlay" />
        <div className="rd-hero-content container">
          <Link to={-1} className="btn btn-secondary rd-back-btn">
            <ArrowLeft size={18} /> Back
          </Link>
          <div className="rd-hero-info">
            {recipe.cuisine && <span className="tag tag-primary">{recipe.cuisine}</span>}
            <h1 className="rd-title">{recipe.title}</h1>
            <div className="rd-meta">
              {recipe.cook_time && <span className="rd-meta-item"><Clock size={16} /> {recipe.cook_time} min</span>}
              {recipe.servings && <span className="rd-meta-item"><Users size={16} /> {recipe.servings} servings</span>}
              {recipe.difficulty && <span className="rd-meta-item"><ChefHat size={16} /> {recipe.difficulty}</span>}
              {recipe.cuisine && <span className="rd-meta-item"><Globe size={16} /> {recipe.cuisine}</span>}
            </div>
          </div>
        </div>
      </div>

      <div className="container rd-body">
        <div className="rd-actions animate-fade-in-up">
          <button className={`btn ${saved ? 'btn-primary' : 'btn-secondary'}`} onClick={toggleSave}>
            {saved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
            {saved ? 'Saved' : 'Save Recipe'}
          </button>
          <button className="btn btn-secondary" onClick={handleShare}>
            <Share2 size={18} /> Share
          </button>
        </div>

        <div className="rd-grid">
          <div className="rd-main">
            {/* Ingredients */}
            <section className="rd-section glass animate-fade-in-up stagger-1">
              <h2 className="rd-section-title">🧂 Ingredients</h2>
              <ul className="rd-ingredients-list">
                {ingredients.map((ing, i) => (
                  <li key={i} className="rd-ingredient-item">
                    <CheckCircle size={16} />
                    <span>{ing}</span>
                  </li>
                ))}
              </ul>
            </section>

            {/* Instructions */}
            <section className="rd-section glass animate-fade-in-up stagger-2">
              <h2 className="rd-section-title">📝 Instructions</h2>
              <ol className="rd-steps-list">
                {steps.map((step, i) => (
                  <li
                    key={i}
                    className={`rd-step-item ${checkedSteps[i] ? 'rd-step-done' : ''}`}
                    onClick={() => toggleStep(i)}
                  >
                    <div className="rd-step-number">{i + 1}</div>
                    <p>{step}</p>
                  </li>
                ))}
              </ol>
            </section>
          </div>

          <div className="rd-sidebar">
            {/* Quick Info */}
            <div className="rd-info-card glass animate-fade-in-up stagger-3">
              <h3>Quick Info</h3>
              <div className="rd-info-grid">
                <div className="rd-info-item">
                  <span className="rd-info-label">Prep Time</span>
                  <span className="rd-info-value">{recipe.prep_time || '—'} min</span>
                </div>
                <div className="rd-info-item">
                  <span className="rd-info-label">Cook Time</span>
                  <span className="rd-info-value">{recipe.cook_time || '—'} min</span>
                </div>
                <div className="rd-info-item">
                  <span className="rd-info-label">Total Time</span>
                  <span className="rd-info-value">{recipe.total_time || '—'} min</span>
                </div>
                <div className="rd-info-item">
                  <span className="rd-info-label">Servings</span>
                  <span className="rd-info-value">{recipe.servings || '—'}</span>
                </div>
              </div>
            </div>

            {/* Rating */}
            <div className="rd-rating-card glass animate-fade-in-up stagger-4">
              <h3>Rate this Recipe</h3>
              <div className="rd-stars">
                {[1, 2, 3, 4, 5].map(s => (
                  <button
                    key={s}
                    className={`rd-star ${s <= (hoverRating || rating) ? 'rd-star-active' : ''}`}
                    onClick={() => { setRating(s); toast.success(`Rated ${s} star${s > 1 ? 's' : ''}! ⭐`); }}
                    onMouseEnter={() => setHoverRating(s)}
                    onMouseLeave={() => setHoverRating(0)}
                  >
                    <Star size={24} fill={s <= (hoverRating || rating) ? 'currentColor' : 'none'} />
                  </button>
                ))}
              </div>
              {rating > 0 && <p className="rd-rating-text">You rated this {rating}/5</p>}
            </div>

            {recipe.source_url && (
              <a href={recipe.source_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary rd-source-btn">
                View Original Source
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
