import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import IngredientInput from '../components/home/IngredientInput';
import { Sparkles, Clock, Globe, Leaf, Users, ArrowRight, ChefHat } from 'lucide-react';
import './Dashboard.css';

const CUISINES = ['', 'Indian', 'South Indian Recipes', 'North Indian Recipes', 'Chinese', 'Italian Recipes', 'Continental', 'Thai', 'Mexican', 'Bengali Recipes', 'Punjabi', 'Andhra', 'Kerala Recipes', 'Chettinad', 'Maharashtrian Recipes', 'Gujarati Recipes'];
const DIETS = ['', 'vegetarian', 'vegan', 'gluten-free', 'keto'];

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [ingredients, setIngredients] = useState([]);
  const [timeLimit, setTimeLimit] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [diet, setDiet] = useState('');
  const [servings, setServings] = useState('');

  const handleGetRecommendations = () => {
    if (ingredients.length === 0) {
      toast.error('Please add at least one ingredient');
      return;
    }

    const params = new URLSearchParams();
    params.set('ingredients', ingredients.join(','));
    if (timeLimit) params.set('timeLimit', timeLimit);
    if (cuisine) params.set('cuisine', cuisine);
    if (diet) params.set('diet', diet);
    if (servings) params.set('servings', servings);

    navigate(`/recommendations?${params.toString()}`);
  };

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  return (
    <div className="page">
      <div className="dashboard-glow" />
      <div className="container">
        <div className="dashboard-header animate-fade-in-up">
          <div>
            <p className="dashboard-greeting">{greeting()},</p>
            <h1 className="dashboard-title">
              {user?.name?.split(' ')[0] || 'Chef'} <span className="wave-emoji">👋</span>
            </h1>
            <p className="dashboard-subtitle">What would you like to cook today?</p>
          </div>
        </div>

        <div className="dashboard-main">
          <div className="dashboard-input-section animate-fade-in-up stagger-1">
            <div className="input-section-card glass">
              <div className="input-section-header">
                <div className="input-section-icon">
                  <ChefHat size={24} />
                </div>
                <div>
                  <h2>What's in your kitchen?</h2>
                  <p>Add the ingredients you have available</p>
                </div>
              </div>

              <IngredientInput ingredients={ingredients} onChange={setIngredients} />

              <div className="filters-section">
                <h3 className="filters-title">
                  <Sparkles size={16} /> Filters <span className="filters-optional">(optional)</span>
                </h3>
                <div className="filters-grid">
                  <div className="input-group">
                    <label><Clock size={14} /> Max Cook Time</label>
                    <input
                      type="number"
                      className="input-field"
                      placeholder="e.g., 30 mins"
                      value={timeLimit}
                      onChange={e => setTimeLimit(e.target.value)}
                    />
                  </div>
                  <div className="input-group">
                    <label><Globe size={14} /> Cuisine</label>
                    <select className="input-field" value={cuisine} onChange={e => setCuisine(e.target.value)}>
                      {CUISINES.map(c => (
                        <option key={c} value={c}>{c || 'Any Cuisine'}</option>
                      ))}
                    </select>
                  </div>
                  <div className="input-group">
                    <label><Leaf size={14} /> Diet</label>
                    <select className="input-field" value={diet} onChange={e => setDiet(e.target.value)}>
                      {DIETS.map(d => (
                        <option key={d} value={d}>{d ? d.charAt(0).toUpperCase() + d.slice(1) : 'No Preference'}</option>
                      ))}
                    </select>
                  </div>
                  <div className="input-group">
                    <label><Users size={14} /> Servings</label>
                    <input
                      type="number"
                      className="input-field"
                      placeholder="e.g., 4"
                      value={servings}
                      onChange={e => setServings(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <button
                className="btn btn-primary btn-lg dashboard-cta"
                onClick={handleGetRecommendations}
                disabled={ingredients.length === 0}
              >
                <Sparkles size={20} />
                Get AI Recommendations
                <ArrowRight size={20} />
              </button>
            </div>
          </div>

          <div className="dashboard-sidebar animate-fade-in-up stagger-2">
            <div className="quick-add-card glass">
              <h3>Quick Add</h3>
              <p>Popular ingredients to get started</p>
              <div className="quick-tags">
                {['chicken', 'rice', 'onion', 'tomato', 'garlic', 'potato', 'paneer', 'dal', 'ginger', 'coconut', 'egg', 'butter'].map(ing => (
                  <button
                    key={ing}
                    className={`quick-tag ${ingredients.includes(ing) ? 'quick-tag-active' : ''}`}
                    onClick={() => {
                      if (ingredients.includes(ing)) {
                        setIngredients(ingredients.filter(i => i !== ing));
                      } else {
                        setIngredients([...ingredients, ing]);
                      }
                    }}
                  >
                    {ing}
                  </button>
                ))}
              </div>
            </div>

            <div className="tip-card glass">
              <div className="tip-icon">💡</div>
              <h3>Pro Tip</h3>
              <p>Add 3-5 ingredients for the best recommendations. The more you add, the better the AI can match recipes!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
