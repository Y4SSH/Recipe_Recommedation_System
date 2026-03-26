import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import IngredientInput from '../components/home/IngredientInput';
import { Sparkles, Clock, Globe, Leaf, Users, ArrowRight, Settings, ChevronDown, ChevronUp } from 'lucide-react';
import './Dashboard.css';

const CUISINES = ['', 'Indian', 'South Indian Recipes', 'North Indian Recipes', 'Chinese', 'Italian Recipes', 'Continental', 'Thai', 'Mexican', 'Bengali Recipes', 'Punjabi', 'Andhra', 'Kerala Recipes', 'Chettinad', 'Maharashtrian Recipes', 'Gujarati Recipes'];
const DIETS = ['', 'vegetarian', 'vegan', 'gluten-free', 'keto'];

const QUICK_TAGS = {
  'neutral': ['chicken', 'rice', 'onion', 'tomato', 'garlic', 'potato', 'paneer', 'dal', 'ginger', 'coconut', 'egg', 'fish'],
  'veg': ['paneer', 'rice', 'onion', 'tomato', 'garlic', 'potato', 'dal', 'ginger', 'coconut', 'mushroom', 'spinach', 'butter'],
  'non-veg': ['chicken', 'egg', 'fish', 'mutton', 'rice', 'onion', 'garlic', 'ginger', 'tomato', 'potato', 'coconut', 'butter']
};

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [ingredients, setIngredients] = useState([]);
  const [dietMode, setDietMode] = useState('neutral');
  const [timeLimit, setTimeLimit] = useState('');
  const [servings, setServings] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [optionsOpen, setOptionsOpen] = useState(false);

  const handleGetRecommendations = () => {
    if (ingredients.length === 0) {
      toast.error('Please add at least one ingredient');
      return;
    }

    const params = new URLSearchParams();
    params.set('ingredients', ingredients.join(','));
    
    if (timeLimit) params.set('timeLimit', timeLimit);
    if (servings) params.set('servings', servings);
    if (cuisine) params.set('cuisine', cuisine);
    
    if (dietMode === 'veg') {
      params.set('diet', 'vegetarian');
    }

    navigate(`/recommendations?${params.toString()}`);
  };

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  return (
    <div className="page dashboard-abstract-page">
      {/* Abstract Background Elements */}
      <div className="dashboard-grid-overlay" />
      <div className="dashboard-orb dashboard-orb-1" />
      <div className="dashboard-orb dashboard-orb-2" />
      <div className="dashboard-orb-3" />

      <div className="container chat-layout-container">
        
        <div className="chat-header animate-fade-in-up">
          <h1>{greeting()}, {user?.name?.split(' ')[0] || 'Chef'} <span className="wave-emoji">👋</span></h1>
          <p>What would you like to cook today?</p>
        </div>

        <div className="chat-main animate-fade-in-up stagger-1">
          
          <div 
            className="chat-input-bar"
            style={{ marginBottom: ingredients.length > 0 ? '56px' : '0', transition: 'margin 0.2s ease-out' }}
          >
             <div className="chat-diet-compact">
               <button 
                 className={`chat-diet-btn ${dietMode === 'neutral' ? 'active-neutral' : ''}`}
                 onClick={() => setDietMode('neutral')}
                 title="Any Diet"
               >
                 <Globe size={18} />
               </button>
               <button 
                 className={`chat-diet-btn ${dietMode === 'veg' ? 'active-veg' : ''}`}
                 onClick={() => setDietMode('veg')}
                 title="Vegetarian"
               >
                 <Leaf size={18} />
               </button>
               <button 
                 className={`chat-diet-btn ${dietMode === 'non-veg' ? 'active-nonveg' : ''}`}
                 onClick={() => setDietMode('non-veg')}
                 title="Non-Vegetarian"
               >
                 <span role="img" aria-label="meat">🍗</span>
               </button>
             </div>

             <div className="chat-input-core">
               <IngredientInput ingredients={ingredients} onChange={setIngredients} />
             </div>

             <button 
               className="chat-submit-btn" 
               onClick={handleGetRecommendations}
               disabled={ingredients.length === 0}
             >
               <Sparkles size={20} />
             </button>
          </div>

          <div className="chat-options animate-fade-in-up stagger-2">
             <button 
               className="chat-expand-btn" 
               onClick={() => setOptionsOpen(!optionsOpen)}
             >
               <Settings size={16} />
               <span>Options & Quick Add</span>
               {optionsOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
             </button>

             {optionsOpen && (
               <div className="chat-expanded-content animate-scale-in">
                 
                 <div className="expanded-section">
                   <h3>Quick Add Ingredients</h3>
                   <div className="quick-tags">
                     {QUICK_TAGS[dietMode].map(ing => (
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

                 <div className="expanded-section">
                   <h3>Advanced Filters</h3>
                   <div className="chat-filters-grid">
                     <div className="filter-group">
                       <label><Clock size={14} /> Max Time (min)</label>
                       <input 
                         type="number" 
                         placeholder="e.g. 30" 
                         value={timeLimit} 
                         onChange={e => setTimeLimit(e.target.value)}
                         className="filter-input-text chat-input-styled"
                       />
                     </div>
                     <div className="filter-group">
                       <label><Users size={14} /> Servings</label>
                       <input 
                         type="number" 
                         placeholder="e.g. 2" 
                         value={servings} 
                         onChange={e => setServings(e.target.value)}
                         className="filter-input-text chat-input-styled"
                       />
                     </div>
                     <div className="filter-group">
                       <label><Globe size={14} /> Cuisine</label>
                       <select 
                         value={cuisine} 
                         onChange={e => setCuisine(e.target.value)}
                         className="filter-input-select chat-input-styled"
                       >
                         {CUISINES.map(c => <option key={c} value={c}>{c || 'Any Cuisine'}</option>)}
                       </select>
                     </div>
                   </div>
                 </div>

               </div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
}
