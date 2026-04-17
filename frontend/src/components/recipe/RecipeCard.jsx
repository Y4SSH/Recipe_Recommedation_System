import { Link, useNavigate } from 'react-router-dom';
import { Clock, Users, ChefHat, Bookmark, BookmarkCheck, Star, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
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

export default function RecipeCard({
  recipe,
  recommendation,
  onSaveToggle,
  index = 0,
  compact = false,
  showFeedback = false,
  feedbackState,
  onFeedback,
  showInterestedAction = false,
  interestedLabel = "Let's make it",
  onInterested,
}) {
  const navigate = useNavigate();
  const { isAuthenticated, savedRecipeIds, saveRecipe, unsaveRecipe } = useAuth();

  const r = recipe || recommendation?.recipe;
  if (!r) return null;
  const saved = savedRecipeIds.includes(r.id);

  const cleanTitle = r.title ? r.title.replace(/\s*[Rr]ecipe\s*$/i, '') : '';
  const score = recommendation?.score;
  const available = recommendation?.available_ingredients || [];
  const missing = recommendation?.missing_ingredients || [];
  const reason = recommendation?.reason;
  const explanation = recommendation?.explanation || recommendation?.modifications || [];
  const cookTime = r.cook_time || r.total_time;
  const difficulty = r.difficulty || 'Medium';
  const variantType = r.variant_type;
  const cookingMethod = r.cooking_method;
  const proteinType = r.protein_type;
  const baseRecipe = r.base_recipe;

  const imageUrl = getLocalImage(cleanTitle); // strictly local only

  let dietType = null;
  try {
    const tgs = JSON.parse(r.tags || '[]');
    if (tgs.includes('veg') || tgs.includes('vegetarian')) dietType = 'veg';
    else if (tgs.includes('non-veg')) dietType = 'non-veg';
  } catch (e) {
    if (r.tags?.includes('veg')) dietType = 'veg';
  }

  const getScoreClass = (s) => {
    if (s >= 70) return 'score-high';
    if (s >= 40) return 'score-medium';
    return 'score-low';
  };

  const handleSave = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (saved) {
      await unsaveRecipe(r.id);
    } else {
      await saveRecipe(r.id);
    }
    onSaveToggle?.();
  };

  const handleFeedbackClick = (e, accepted) => {
    e.preventDefault();
    e.stopPropagation();
    if (!onFeedback || !r?.id) return;
    onFeedback(r.id, accepted);
  };

  const handleInterestedClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!onInterested || !r?.id) return;
    onInterested(r.id);
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
      className={`recipe-card animate-fade-in-up ${compact ? 'recipe-card-compact' : ''}`}
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      <div className="recipe-card-image skeleton">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={cleanTitle}
            loading="lazy"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.parentElement.style.background = getCuisineColor(r.cuisine);
            }}
          />
        ) : (
          <div className="recipe-card-placeholder" style={{ background: getCuisineColor(r.cuisine) }}>
            <ChefHat size={40} />
          </div>
        )}
        <div className="recipe-card-overlay" />

        {compact && score !== undefined && (
          <div className={`score-badge ${getScoreClass(score)} recipe-score-float recipe-score-float-compact`}>
            <Star size={12} />
            {score.toFixed(0)}%
          </div>
        )}

        {dietType === 'veg' && (
          <div className="recipe-diet-badge" style={{ position: 'absolute', top: 12, left: 12, zIndex: 10, background: '#fff', padding: 4, borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ border: '2px solid #10b981', width: 20, height: 20, borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: 10, height: 10, background: '#10b981', borderRadius: '50%' }}></div>
            </div>
          </div>
        )}
        {dietType === 'non-veg' && (
          <div className="recipe-diet-badge" style={{ position: 'absolute', top: 12, left: 12, zIndex: 10, background: '#fff', padding: 4, borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ border: '2px solid #ef4444', width: 20, height: 20, borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: 10, height: 10, background: '#ef4444', borderRadius: '50%' }}></div>
            </div>
          </div>
        )}

        <button className={`recipe-save-btn ${saved ? 'recipe-saved' : ''}`} onClick={handleSave}>
          {saved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
        </button>

        {!compact && score !== undefined && (
          <div className={`score-badge ${getScoreClass(score)} recipe-score-float`}>
            <Star size={12} />
            {score.toFixed(0)}%
          </div>
        )}

        {showInterestedAction && (
          <button type="button" className="recipe-interest-btn recipe-interest-btn-overlay" onClick={handleInterestedClick}>
            {interestedLabel}
          </button>
        )}
      </div>

      <div className="recipe-card-body">
        <div className="recipe-card-heading">
          <h3 className="recipe-card-title">{cleanTitle}</h3>
          {!compact && score !== undefined && (
            <div className={`score-badge ${getScoreClass(score)} recipe-score-inline`}>
              <Star size={12} />
              {score.toFixed(0)}%
            </div>
          )}
        </div>

        {reason && <p className="recipe-card-reason">{reason}</p>}

        {!compact && explanation.length > 0 ? (
          <ul className="recipe-card-explanation">
            {explanation.slice(0, 3).map((line, idx) => (
              <li key={idx}>{line}</li>
            ))}
          </ul>
        ) : null}

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

        <div className="recipe-card-meta-tags">
          {variantType && variantType !== 'standard' && (
            <span className="tag tag-neutral">Variant: {variantType}</span>
          )}
          {cookingMethod && cookingMethod !== 'standard' && (
            <span className="tag tag-neutral">Method: {cookingMethod.replace(/_/g, ' ')}</span>
          )}
          {proteinType && (
            <span className="tag tag-neutral">Protein: {proteinType.replace(/_/g, ' ')}</span>
          )}
          {baseRecipe && baseRecipe !== r.title && (
            <span className="tag tag-neutral">Base: {baseRecipe}</span>
          )}
        </div>

        {(available.length > 0 || missing.length > 0) && (
          <div className="recipe-ingredient-section">
            {available.length > 0 && (
              <div className="ingredient-group">
                <div className="ingredient-group-label">Available</div>
                <div className="ingredient-chips">
                  {available.slice(0, compact ? 1 : 4).map((ing, i) => (
                    <span key={i} className="tag tag-success">{ing}</span>
                  ))}
                  {available.length > (compact ? 1 : 4) && (
                    <span className="tag tag-neutral">+{available.length - (compact ? 1 : 4)}</span>
                  )}
                </div>
              </div>
            )}
            {missing.length > 0 && (
              <div className="ingredient-group">
                <div className="ingredient-group-label">Missing</div>
                <div className="ingredient-chips">
                  {missing.slice(0, compact ? 1 : 3).map((ing, i) => (
                    <span key={i} className="tag tag-error">{ing}</span>
                  ))}
                  {missing.length > (compact ? 1 : 3) && (
                    <span className="tag tag-neutral">+{missing.length - (compact ? 1 : 3)}</span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {showFeedback && (
          <div className="recipe-feedback-row">
            <button
              type="button"
              className={`recipe-feedback-btn ${feedbackState === 'helpful' ? 'active' : ''}`}
              onClick={(e) => handleFeedbackClick(e, true)}
            >
              <ThumbsUp size={14} /> Useful
            </button>
            <button
              type="button"
              className={`recipe-feedback-btn ${feedbackState === 'not_helpful' ? 'active' : ''}`}
              onClick={(e) => handleFeedbackClick(e, false)}
            >
              <ThumbsDown size={14} /> Not Useful
            </button>
          </div>
        )}
      </div>
    </Link>
  );
}
