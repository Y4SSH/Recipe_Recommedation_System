import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Clock, CheckCircle2, PlayCircle, RotateCcw, ListChecks, CircleDashed, ChevronRight, X } from 'lucide-react';
import api from '../services/api';
import { useToast } from '../context/ToastContext';
import './MyRecipes.css';

const parseList = (value) => {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) {
      return parsed.map(item => typeof item === 'string' ? item : item?.name || String(item)).filter(Boolean);
    }
  } catch {
    // fall back below
  }
  return String(value).split(',').map(item => item.trim()).filter(Boolean);
};

const getStatusLabel = (status) => {
  if (status === 'in_progress') return 'In Progress';
  if (status === 'completed') return 'Completed';
  return 'Interested';
};

const getStatusClass = (status) => {
  if (status === 'in_progress') return 'status-active';
  if (status === 'completed') return 'status-completed';
  return 'status-interested';
};

export default function MyRecipes() {
  const toast = useToast();
  const [journeys, setJourneys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editorJourney, setEditorJourney] = useState(null);
  const [selectedIngredients, setSelectedIngredients] = useState([]);
  const [selectedSteps, setSelectedSteps] = useState([]);
  const [saving, setSaving] = useState(false);

  const loadJourneys = async () => {
    setLoading(true);
    try {
      const data = await api.getMyRecipes();
      setJourneys(data || []);
    } catch (err) {
      toast.error(err.message || 'Unable to load My Recipes');
      setJourneys([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJourneys();
  }, []);

  const activeJourney = useMemo(
    () => journeys.find(journey => journey.status === 'in_progress') || null,
    [journeys]
  );

  const ingredientOptions = parseList(editorJourney?.recipe?.ingredients);
  const stepOptions = parseList(editorJourney?.recipe?.steps);

  const liveProgress = useMemo(() => {
    if (!editorJourney) return 0;
    const parts = [];
    if (ingredientOptions.length > 0) {
      parts.push(selectedIngredients.length / ingredientOptions.length);
    }
    if (stepOptions.length > 0) {
      parts.push(selectedSteps.length / stepOptions.length);
    }
    if (parts.length === 0) return editorJourney.progress_percent || 0;
    return Math.round((parts.reduce((sum, part) => sum + part, 0) / parts.length) * 100);
  }, [editorJourney, ingredientOptions.length, stepOptions.length, selectedIngredients.length, selectedSteps.length]);

  const openEditor = async (journey, shouldStart = false) => {
    try {
      let nextJourney = journey;
      if (shouldStart && journey.status !== 'in_progress') {
        nextJourney = await api.startMyRecipe(journey.recipe_id);
      }

      setEditorJourney(nextJourney);
      setSelectedIngredients((nextJourney.ingredients_gathered || []).map(Number).filter(Number.isFinite));
      setSelectedSteps((nextJourney.steps_completed || []).map(Number).filter(Number.isFinite));
      setJourneys(prev => prev.map(item => (item.id === nextJourney.id ? nextJourney : item)));
    } catch (err) {
      toast.error(err.message || 'Finish the active recipe before starting another one');
    }
  };

  const toggleSelected = (current, value) => {
    return current.includes(value) ? current.filter(item => item !== value) : [...current, value];
  };

  const saveProgress = async (markCompleted = false) => {
    if (!editorJourney) return;

    setSaving(true);
    try {
      const updated = await api.updateMyRecipeProgress(editorJourney.recipe_id, {
        ingredients_gathered: selectedIngredients,
        steps_completed: selectedSteps,
        mark_completed: markCompleted,
      });

      setJourneys(prev => prev.map(item => (item.id === updated.id ? updated : item)));
      setEditorJourney(updated);
      toast.success(markCompleted ? 'Recipe marked as completed' : 'Progress saved');
    } catch (err) {
      toast.error(err.message || 'Unable to save progress');
    } finally {
      setSaving(false);
      loadJourneys();
    }
  };

  const closeEditor = () => {
    setEditorJourney(null);
    setSelectedIngredients([]);
    setSelectedSteps([]);
  };

  const canComplete = ingredientOptions.length > 0 && stepOptions.length > 0
    ? selectedIngredients.length === ingredientOptions.length && selectedSteps.length === stepOptions.length
    : liveProgress >= 100;

  return (
    <div className="page">
      <div className="container">
        <div className="page-header animate-fade-in-up">
          <h1>
            <BookOpen size={28} style={{ marginRight: 12 }} />
            My Recipes
          </h1>
          <p>Track recipes you want to cook, manage one active recipe, and mark progress as you go.</p>
        </div>

        {editorJourney && (
          <div className="my-recipes-editor glass animate-fade-in-up stagger-1">
            <div className="my-recipes-editor-head">
              <div>
                <span className="editor-kicker">Cooking Session</span>
                <h2>{editorJourney.recipe?.title || 'Recipe'}</h2>
                <p>Select ingredients you have gathered and tick off the steps you have finished.</p>
              </div>
              <button className="btn btn-ghost" onClick={closeEditor}>
                <X size={16} /> Close
              </button>
            </div>

            <div className="editor-progress-bar">
              <div className="editor-progress-fill" style={{ width: `${liveProgress}%` }} />
            </div>
            <div className="editor-progress-meta">
              <span>{liveProgress}% complete</span>
              <span>{selectedIngredients.length}/{ingredientOptions.length || 0} ingredients</span>
              <span>{selectedSteps.length}/{stepOptions.length || 0} steps</span>
            </div>

            <div className="editor-grid">
              <section className="editor-panel">
                <div className="editor-panel-head">
                  <h3>Ingredients Gathered</h3>
                  <span>Manual check</span>
                </div>
                <div className="checklist">
                  {ingredientOptions.length === 0 ? (
                    <p className="empty-helper">No ingredient data found.</p>
                  ) : ingredientOptions.map((ingredient, index) => (
                    <label key={`${ingredient}-${index}`} className="check-item">
                      <input
                        type="checkbox"
                        checked={selectedIngredients.includes(index)}
                        onChange={() => setSelectedIngredients(current => toggleSelected(current, index))}
                      />
                      <span>{ingredient}</span>
                    </label>
                  ))}
                </div>
              </section>

              <section className="editor-panel">
                <div className="editor-panel-head">
                  <h3>Steps Completed</h3>
                  <span>Manual check</span>
                </div>
                <div className="checklist">
                  {stepOptions.length === 0 ? (
                    <p className="empty-helper">No step data found.</p>
                  ) : stepOptions.map((step, index) => (
                    <label key={`${step}-${index}`} className="check-item">
                      <input
                        type="checkbox"
                        checked={selectedSteps.includes(index)}
                        onChange={() => setSelectedSteps(current => toggleSelected(current, index))}
                      />
                      <span>{step}</span>
                    </label>
                  ))}
                </div>
              </section>
            </div>

            <div className="editor-actions">
              <button className="btn btn-secondary" onClick={() => saveProgress(false)} disabled={saving}>
                <RotateCcw size={16} /> {saving ? 'Saving...' : 'Save Progress'}
              </button>
              <button className="btn btn-primary" onClick={() => saveProgress(true)} disabled={saving || !canComplete}>
                <CheckCircle2 size={16} /> {editorJourney.status === 'completed' ? 'Completed' : 'Mark Completed'}
              </button>
            </div>
          </div>
        )}

        <div className="my-recipes-list">
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner" />
              <p className="loading-text">Loading your recipe journey...</p>
            </div>
          ) : journeys.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><CircleDashed size={32} /></div>
              <h3>No recipes yet</h3>
              <p>Open recommendations, mark a recipe as interested, and it will appear here.</p>
              <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 16 }}>
                Explore Recipes <ChevronRight size={16} />
              </Link>
            </div>
          ) : (
            <div className="my-recipes-grid animate-fade-in">
              {journeys.map((journey, index) => {
                const ingredientOptionsLocal = parseList(journey.recipe?.ingredients);
                const stepOptionsLocal = parseList(journey.recipe?.steps);
                const ingredientProgress = ingredientOptionsLocal.length > 0
                  ? Math.round(((journey.ingredients_gathered || []).length / ingredientOptionsLocal.length) * 100)
                  : 0;
                const stepProgress = stepOptionsLocal.length > 0
                  ? Math.round(((journey.steps_completed || []).length / stepOptionsLocal.length) * 100)
                  : 0;
                const recipeProgress = journey.progress_percent || 0;
                const isActive = journey.status === 'in_progress';
                const isCompleted = journey.status === 'completed';
                const canStartThis = !activeJourney || activeJourney.recipe_id === journey.recipe_id || isActive || isCompleted;

                return (
                  <article key={journey.id} className={`my-recipe-card animate-fade-in-up stagger-${Math.min(index + 1, 4)}`}>
                    <div className="my-recipe-card-head">
                      <div>
                        <span className={`status-pill ${getStatusClass(journey.status)}`}>{getStatusLabel(journey.status)}</span>
                        <h3>{journey.recipe?.title || 'Recipe'}</h3>
                        <p>{journey.recipe?.cuisine || 'Global cuisine'} · {journey.recipe?.total_time || 0} min</p>
                      </div>
                      <Link to={`/recipe/${journey.recipe_id}`} className="btn btn-ghost btn-sm">
                        View
                      </Link>
                    </div>

                    <div className="mini-progress">
                      <div className="mini-progress-fill" style={{ width: `${recipeProgress}%` }} />
                    </div>
                    <div className="my-recipe-stats">
                      <span><ListChecks size={14} /> {journey.steps_completed?.length || 0}/{stepOptionsLocal.length || 0} steps</span>
                      <span><Clock size={14} /> {journey.ingredients_gathered?.length || 0}/{ingredientOptionsLocal.length || 0} ingredients</span>
                      <span><PlayCircle size={14} /> {recipeProgress}% overall</span>
                    </div>

                    <div className="my-recipe-card-actions">
                      {isCompleted ? (
                        <button className="btn btn-secondary btn-sm" onClick={() => openEditor(journey, false)}>
                          <CheckCircle2 size={14} /> Completed
                        </button>
                      ) : isActive ? (
                        <button className="btn btn-primary btn-sm" onClick={() => openEditor(journey, false)}>
                          <PlayCircle size={14} /> Continue cooking
                        </button>
                      ) : (
                        <button className="btn btn-primary btn-sm" onClick={() => openEditor(journey, true)} disabled={!canStartThis}>
                          <PlayCircle size={14} /> Let's start
                        </button>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}