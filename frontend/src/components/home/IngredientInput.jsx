import { useState, useRef } from 'react';
import { X, Plus } from 'lucide-react';
import './IngredientInput.css';

const SUGGESTIONS = [
  'chicken', 'rice', 'onion', 'tomato', 'garlic', 'ginger', 'potato',
  'paneer', 'milk', 'butter', 'oil', 'salt', 'cumin', 'turmeric',
  'coriander', 'chilli', 'lemon', 'coconut', 'yogurt', 'egg',
  'flour', 'sugar', 'carrot', 'spinach', 'peas', 'beans',
  'mushroom', 'capsicum', 'cauliflower', 'broccoli', 'cheese',
  'cream', 'dal', 'ghee', 'mustard', 'pepper', 'cinnamon',
  'cardamom', 'cloves', 'bay leaf', 'mint', 'curry leaves',
  'tamarind', 'jaggery', 'cashew', 'almond', 'raisin',
  'prawn', 'fish', 'mutton', 'lamb', 'corn', 'bread',
  'noodles', 'pasta', 'soy sauce', 'vinegar', 'honey',
];

export default function IngredientInput({ ingredients, onChange }) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null);

  const filtered = inputValue.trim()
    ? SUGGESTIONS.filter(
        s => s.includes(inputValue.toLowerCase()) && !ingredients.includes(s)
      ).slice(0, 8)
    : [];

  const addIngredient = (value) => {
    const v = value.trim().toLowerCase();
    if (v && !ingredients.includes(v)) {
      onChange([...ingredients, v]);
    }
    setInputValue('');
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const removeIngredient = (ing) => {
    onChange(ingredients.filter(i => i !== ing));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (inputValue.trim()) addIngredient(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && ingredients.length > 0) {
      removeIngredient(ingredients[ingredients.length - 1]);
    }
  };

  return (
    <div className="ingredient-input-wrapper">
      <div className="ingredient-input-box" onClick={() => inputRef.current?.focus()}>
        <div className="ingredient-tags-area">
          {ingredients.map((ing, i) => (
            <span key={ing} className="ingredient-tag animate-scale-in" style={{ animationDelay: `${i * 0.03}s` }}>
              {ing}
              <button onClick={(e) => { e.stopPropagation(); removeIngredient(ing); }} className="ingredient-tag-remove">
                <X size={12} />
              </button>
            </span>
          ))}
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => { setInputValue(e.target.value); setShowSuggestions(true); }}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={ingredients.length === 0 ? 'Type ingredients like chicken, rice, tomato...' : 'Add more...'}
            className="ingredient-text-input"
          />
        </div>
        {inputValue.trim() && (
          <button className="ingredient-add-btn" onClick={() => addIngredient(inputValue)}>
            <Plus size={18} />
          </button>
        )}
      </div>

      {showSuggestions && filtered.length > 0 && (
        <div className="ingredient-suggestions">
          {filtered.map(s => (
            <button key={s} className="suggestion-item" onMouseDown={() => addIngredient(s)}>
              <Plus size={14} />
              {s}
            </button>
          ))}
        </div>
      )}

      {ingredients.length > 0 && (
        <div className="ingredient-count">
          <span>{ingredients.length} ingredient{ingredients.length !== 1 ? 's' : ''} added</span>
          <button className="btn btn-ghost btn-sm" onClick={() => onChange([])}>Clear all</button>
        </div>
      )}
    </div>
  );
}
