import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, Users, ChefHat, Bookmark, BookmarkCheck, Star } from 'lucide-react';
import api from '../../services/api';
import './RecipeCard.css';

const knownImages = import.meta.glob('../../assets/images/recipes/*.{jpg,jpeg,png,webp}', { eager: true, as: 'url' });

const getLocalImage = (title) => {
  if (!title) return null;
  const t = title.replace(/\s*[Rr]ecipe\s*$/i, '').trim().toLowerCase();
  for (const [path, url] of Object.entries(knownImages)) {
    const fileNameBase = path.split('/').pop().split('.')[0].toLowerCase();
    if (fileNameBase === t || t.includes(fileNameBase) || fileNameBase.includes(t)) {
      return url;
    }
  }
  return null;
};

export default function RecipeCard({ recipe, recommendation, onSaveToggle, index = 0 }) {
  const [saved, setSaved] = useState(api.isRecipeSaved(recipe?.id));

  const r = recipe || recommendation?.recipe;
  if (!r) return null;

  const cleanTitle = r.title ? r.title.replace(/\s*[Rr]ecipe\s*$/i, '') : '';
  const score = recommendation?.score;
  const available = recommendation?.available_ingredients || [];
  const missing = recommendation?.missing_ingredients || [];
  const reason = recommendation?.reason;

  const imageUrl = getLocalImage(cleanTitle) || r.image_url || null;
  const cookTime = r.cook_time || r.total_time;
  const difficulty = r.difficulty || 'Medium';

  const getScoreClass = (s) => {
    if (s >= 70) return 'score-high';
    if (s >= 40) return 'score-medium';
    return 'score-low';
  };

  const handleSave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (saved) {
      api.unsaveRecipe(r.id);
      setSaved(false);
    } else {
      api.saveRecipe(r.id);
      setSaved(true);
    }
    onSaveToggle?.();
  };

  const getCuisineColor = (c) => {
    if (!c) return 'var(--primary)';
    const cuisine = c.toLowerCase();
    if (cuisine.includes('south indian') || cuisine.includes('kerala') || cuisine.includes('andhra')) return '#10b981';
    if (cuisine.includes('north indian') || cuisine.includes('punjabi')) return '#f59e0b';
    if (cuisine.includes('chinese') || cuisine.includes('thai')) return '#ef4444';
    if (cuisine.includes('continental') || cuisine.includes('italian') || cuisine.includes('mexican')) return '#3b82f6';
    if (cuisine.includes('bengali') || cuisine.includes('maharashtrian') || cuisine.includes('gujarati')) return '#8b5cf6';
    return 'var(--primary)';
  };

  return (
    <Link
      to={`/recipe/${r.id}`}
      className="recipe-card animate-fade-in-up"
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      <div className="recipe-card-image skeleton">
        {imageUrl ? (
          <img src={imageUrl} alt={cleanTitle} loading="lazy" onError={(e) => {
            e.target.style.display = 'none';
            e.target.parentElement.style.background = getCuisineColor(r.cuisine);
          }} />
        ) : (
          <div className="recipe-card-placeholder" style={{ background: getCuisineColor(r.cuisine) }}>
            <ChefHat size={40} />
          </div>
        )}
        <div className="recipe-card-overlay" />

        <button className={`recipe-save-btn ${saved ? 'recipe-saved' : ''}`} onClick={handleSave}>
          {saved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
        </button>

        {score !== undefined && (
          <div className={`score-badge ${getScoreClass(score)} recipe-score-float`}>
            <Star size={12} />
            {score.toFixed(0)}%
          </div>
        )}
      </div>

      <div className="recipe-card-body">
        <h3 className="recipe-card-title">{cleanTitle}</h3>

        {reason && <p className="recipe-card-reason">{reason}</p>}

        <div className="recipe-card-meta">
          {cookTime && (
            <span className="recipe-meta-item">
              <Clock size={14} />
              {cookTime} min
            </span>
          )}
          {r.servings && (
            <span className="recipe-meta-item">
              <Users size={14} />
              {r.servings}
            </span>
          )}
          {difficulty && (
            <span className="recipe-meta-item recipe-difficulty">{difficulty}</span>
          )}
        </div>

        {r.cuisine && (
          <span className="tag tag-primary recipe-cuisine-tag">{r.cuisine}</span>
        )}

        {(available.length > 0 || missing.length > 0) && (
          <div className="recipe-card-ingredients">
            {available.length > 0 && (
              <div className="ingredient-chips">
                {available.slice(0, 4).map((ing, i) => (
                  <span key={i} className="tag tag-success">{ing}</span>
                ))}
                {available.length > 4 && (
                  <span className="tag tag-neutral">+{available.length - 4}</span>
                )}
              </div>
            )}
            {missing.length > 0 && (
              <div className="ingredient-chips">
                {missing.slice(0, 3).map((ing, i) => (
                  <span key={i} className="tag tag-error">{ing}</span>
                ))}
                {missing.length > 3 && (
                  <span className="tag tag-neutral">+{missing.length - 3}</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}
