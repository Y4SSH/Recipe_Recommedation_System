import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../services/api';
import IngredientInput from '../components/home/IngredientInput';
import { Sparkles, Clock, Globe, Leaf, Users, Settings, ChevronDown, ChevronUp, RotateCcw, Plus } from 'lucide-react';
import './Dashboard.css';

const CUISINES = [
  { value: '', label: 'Any (Indian dataset)' },
  { value: 'indian', label: 'Indian' },
];
const HEALTH_GOALS = ['', 'high-protein', 'low-calorie', 'balanced'];

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
  const [panelMode, setPanelMode] = useState('ingredients');
  const [budgetLimit, setBudgetLimit] = useState('');
  const [healthGoal, setHealthGoal] = useState('');
  const [wasteMode, setWasteMode] = useState(false);
  const [pantryItems, setPantryItems] = useState([]);
  const [pantryName, setPantryName] = useState('');
  const [pantryDays, setPantryDays] = useState('2');

  const dietLabel = dietMode === 'veg' ? 'veg' : dietMode === 'non-veg' ? 'non-veg' : null;

  useEffect(() => {
    const loadPantry = async () => {
      try {
        const data = await api.getPantry();
        setPantryItems(Array.isArray(data?.items) ? data.items : []);
      } catch {
        // ignore if user has no pantry yet
      }
    };

    loadPantry();
  }, []);

  const persistPantry = async (nextItems) => {
    setPantryItems(nextItems);
    try {
      await api.updatePantry(nextItems);
    } catch {
      // keep UI responsive even if network is intermittent
    }
  };

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
    if (budgetLimit) params.set('budget', budgetLimit);
    if (healthGoal) params.set('healthGoal', healthGoal);
    if (wasteMode) params.set('wasteMode', '1');
    if (wasteMode && pantryItems.length > 0) {
      params.set('pantry', encodeURIComponent(JSON.stringify(pantryItems.slice(0, 20))));
    }
    
    if (dietMode === 'veg') {
      params.set('diet', 'veg');
    } else if (dietMode === 'non-veg') {
      params.set('diet', 'non-veg');
    }

    navigate(`/recommendations?${params.toString()}`);
  };

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const activeFilterChips = [
    dietLabel,
    timeLimit ? `${timeLimit} min` : null,
    servings ? `${servings} servings` : null,
    cuisine ? cuisine : null,
    budgetLimit ? `$${budgetLimit} budget` : null,
    healthGoal ? healthGoal : null,
    wasteMode ? 'Zero-waste' : null,
  ].filter(Boolean);

  const applyPreset = (preset) => {
    setOptionsOpen(true);
    setPanelMode('filters');

    if (preset === 'fast') {
      setTimeLimit('20');
      setHealthGoal('balanced');
      return;
    }

    if (preset === 'healthy') {
      setHealthGoal('high-protein');
      setBudgetLimit('');
      return;
    }

    if (preset === 'budget') {
      setBudgetLimit('8');
      setHealthGoal('balanced');
      return;
    }

    if (preset === 'zeroWaste') {
      setWasteMode(true);
      return;
    }
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
          <div className="chat-hero-badges" aria-label="Product highlights">
            <span className="hero-badge">Hybrid AI</span>
            <span className="hero-badge">Explainable</span>
            <span className="hero-badge">Zero-waste ready</span>
          </div>
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
               aria-expanded={optionsOpen}
               aria-controls="dashboard-options-panel"
               onClick={() => setOptionsOpen(!optionsOpen)}
             >
               <Settings size={16} />
               <span>Cooking Controls</span>
               {optionsOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
             </button>

             <p className="chat-expand-caption">
               Tune time, budget, cuisine, and zero-waste mode without cluttering the main input.
             </p>

             {activeFilterChips.length > 0 && (
               <div className="chat-active-chips" aria-label="Active filters">
                 {activeFilterChips.map((chip) => (
                   <span key={chip} className="tag tag-neutral chat-active-chip">{chip}</span>
                 ))}
                 <button
                   type="button"
                   className="chat-clear-btn"
                   onClick={() => {
                     setTimeLimit('');
                     setServings('');
                     setCuisine('');
                     setBudgetLimit('');
                     setHealthGoal('');
                     setWasteMode(false);
                   }}
                 >
                   <RotateCcw size={14} />
                   Reset
                 </button>
               </div>
             )}

             {optionsOpen && (
               <div id="dashboard-options-panel" className="chat-expanded-content animate-scale-in" aria-live="polite">
                 <div className="options-panel-header">
                   <div>
                     <h2>Cooking Controls</h2>
                     <p>Keep the page clean by switching between ingredient shortcuts and precise filters.</p>
                   </div>
                   <div className="options-panel-badge">Accessible controls</div>
                 </div>

                 <div className="preset-row" aria-label="Quick presets">
                   <button type="button" className="preset-pill" onClick={() => applyPreset('fast')}>Fast meal</button>
                   <button type="button" className="preset-pill" onClick={() => applyPreset('healthy')}>High-protein</button>
                   <button type="button" className="preset-pill" onClick={() => applyPreset('budget')}>Budget friendly</button>
                   <button type="button" className="preset-pill" onClick={() => applyPreset('zeroWaste')}>Zero-waste</button>
                 </div>
                 <div className="panel-switcher" role="tablist" aria-label="Cooking controls sections">
                   <button
                     type="button"
                     role="tab"
                     aria-selected={panelMode === 'ingredients'}
                     className={`panel-switcher-tab ${panelMode === 'ingredients' ? 'active' : ''}`}
                     onClick={() => setPanelMode('ingredients')}
                   >
                     Ingredients
                   </button>
                   <button
                     type="button"
                     role="tab"
                     aria-selected={panelMode === 'filters'}
                     className={`panel-switcher-tab ${panelMode === 'filters' ? 'active' : ''}`}
                     onClick={() => setPanelMode('filters')}
                   >
                     Filters
                   </button>
                 </div>

                 <div className="options-surface">
                   {panelMode === 'ingredients' ? (
                     <section className="options-section">
                       <div className="expanded-section-head compact-head">
                         <h3>Quick Add Ingredients</h3>
                         <span>Tap to toggle</span>
                       </div>
                       <div className="quick-tags quick-tags-compact" role="list" aria-label="Quick add ingredients">
                         {QUICK_TAGS[dietMode].map(ing => (
                           <button
                             key={ing}
                             className={`quick-tag ${ingredients.includes(ing) ? 'quick-tag-active' : ''}`}
                             type="button"
                             aria-pressed={ingredients.includes(ing)}
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
                     </section>
                   ) : (
                     <section className="options-section">
                       <div className="expanded-section-head compact-head">
                         <h3>Advanced Filters</h3>
                         <span>Exact preferences</span>
                       </div>
                       <div className="chat-filters-grid compact-grid">
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
                             {CUISINES.map(c => (
                               <option key={c.value || 'any'} value={c.value}>{c.label}</option>
                             ))}
                           </select>
                         </div>
                         <div className="filter-group">
                           <label>Budget / meal ($)</label>
                           <input
                             type="number"
                             min="1"
                             step="0.5"
                             placeholder="e.g. 8"
                             value={budgetLimit}
                             onChange={e => setBudgetLimit(e.target.value)}
                             className="filter-input-text chat-input-styled"
                           />
                         </div>
                         <div className="filter-group">
                           <label>Health Goal</label>
                           <select
                             value={healthGoal}
                             onChange={e => setHealthGoal(e.target.value)}
                             className="filter-input-select chat-input-styled"
                           >
                             {HEALTH_GOALS.map(g => <option key={g} value={g}>{g || 'Any Goal'}</option>)}
                           </select>
                         </div>
                         <div className="filter-group">
                           <label>Zero-Waste Mode</label>
                           <button
                             type="button"
                             className={`quick-tag ${wasteMode ? 'quick-tag-active' : ''}`}
                             onClick={() => setWasteMode(!wasteMode)}
                             style={{ width: 'fit-content', minWidth: '94px' }}
                           >
                             {wasteMode ? 'On' : 'Off'}
                           </button>
                         </div>
                       </div>

                       {wasteMode && (
                         <div className="pantry-builder">
                           <div className="expanded-section-head compact-head">
                             <h3>Expiring Pantry Items</h3>
                             <span>Stored in your profile</span>
                           </div>
                           <div className="pantry-controls">
                             <input
                               type="text"
                               placeholder="Ingredient"
                               value={pantryName}
                               onChange={e => setPantryName(e.target.value)}
                               className="filter-input-text chat-input-styled"
                             />
                             <input
                               type="number"
                               min="0"
                               max="30"
                               value={pantryDays}
                               onChange={e => setPantryDays(e.target.value)}
                               className="filter-input-text chat-input-styled"
                             />
                             <button
                               type="button"
                               className="quick-tag pantry-add-btn"
                               onClick={() => {
                                 const name = pantryName.trim();
                                 if (!name) return;
                                 const days = Number.parseInt(pantryDays || '0', 10);
                                 const safeDays = Number.isNaN(days) ? 0 : Math.max(0, Math.min(30, days));
                                 const nextItems = [
                                   ...pantryItems.filter((i) => i.name.toLowerCase() !== name.toLowerCase()),
                                   { name, expires_in_days: safeDays },
                                 ];
                                 persistPantry(nextItems);
                                 setPantryName('');
                                 setPantryDays('2');
                               }}
                             >
                               <Plus size={14} />
                               Add Item
                             </button>
                           </div>
                           <div className="quick-tags pantry-item-list">
                             {pantryItems.map((item) => (
                               <button
                                 type="button"
                                 key={`${item.name}-${item.expires_in_days}`}
                                 className="quick-tag quick-tag-active"
                                 onClick={() => {
                                   const nextItems = pantryItems.filter((i) => i.name !== item.name);
                                   persistPantry(nextItems);
                                 }}
                               >
                                 {item.name} ({item.expires_in_days}d) ×
                               </button>
                             ))}
                           </div>
                         </div>
                       )}
                     </section>
                   )}
                 </div>

               </div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
}
