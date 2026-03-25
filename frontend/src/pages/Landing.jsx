import { Link } from 'react-router-dom';
import { ChefHat, Sparkles, Search, Clock, Heart, ArrowRight, Star, Zap, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Landing.css';

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="landing-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-orb hero-orb-1" />
          <div className="hero-orb hero-orb-2" />
          <div className="hero-orb hero-orb-3" />
          <div className="hero-grid" />
        </div>
        <div className="container hero-content">
          <div className="hero-badge animate-fade-in-up stagger-1">
            <Sparkles size={14} />
            AI-Powered Recipe Discovery
          </div>
          <h1 className="hero-title animate-fade-in-up stagger-2">
            Cook Smarter with
            <span className="hero-title-accent"> ChefAI</span>
          </h1>
          <p className="hero-subtitle animate-fade-in-up stagger-3">
            Tell us what's in your kitchen, and our AI will recommend delicious recipes
            you can make right now. No more food waste, no more recipe hunting.
          </p>
          <div className="hero-actions animate-fade-in-up stagger-4">
            <Link to={isAuthenticated ? '/dashboard' : '/register'} className="btn btn-primary btn-lg">
              {isAuthenticated ? 'Go to Dashboard' : 'Start Cooking'}
              <ArrowRight size={20} />
            </Link>
            <Link to="/explore" className="btn btn-secondary btn-lg">
              <Search size={18} />
              Explore Recipes
            </Link>
          </div>
          <div className="hero-stats animate-fade-in-up stagger-5">
            <div className="hero-stat">
              <span className="hero-stat-number">50K+</span>
              <span className="hero-stat-label">Recipes</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-number">100+</span>
              <span className="hero-stat-label">Cuisines</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-number">AI</span>
              <span className="hero-stat-label">Powered</span>
            </div>
          </div>
        </div>

        {/* Floating food emojis */}
        <div className="hero-floating">
          <span className="float-item" style={{ top: '15%', left: '8%', animationDelay: '0s' }}>🍛</span>
          <span className="float-item" style={{ top: '25%', right: '10%', animationDelay: '1s' }}>🥘</span>
          <span className="float-item" style={{ bottom: '30%', left: '12%', animationDelay: '2s' }}>🍲</span>
          <span className="float-item" style={{ bottom: '20%', right: '8%', animationDelay: '0.5s' }}>🌶️</span>
          <span className="float-item" style={{ top: '50%', right: '15%', animationDelay: '1.5s' }}>🧄</span>
        </div>
      </section>

      {/* How it Works */}
      <section className="how-it-works">
        <div className="container">
          <div className="section-header animate-fade-in-up">
            <span className="section-tag">
              <Zap size={14} /> Simple Process
            </span>
            <h2 className="section-title">How ChefAI Works</h2>
            <p className="section-subtitle">Three simple steps to your perfect meal</p>
          </div>

          <div className="steps-grid">
            <div className="step-card animate-fade-in-up stagger-1">
              <div className="step-number">01</div>
              <div className="step-icon">
                <Search size={28} />
              </div>
              <h3>Enter Your Ingredients</h3>
              <p>Tell us what you have in your kitchen. Add as many ingredients as you want.</p>
            </div>
            <div className="step-connector">
              <ArrowRight size={24} />
            </div>
            <div className="step-card animate-fade-in-up stagger-2">
              <div className="step-number">02</div>
              <div className="step-icon">
                <Sparkles size={28} />
              </div>
              <h3>AI Matches Recipes</h3>
              <p>Our AI engine finds the best recipes that match your available ingredients.</p>
            </div>
            <div className="step-connector">
              <ArrowRight size={24} />
            </div>
            <div className="step-card animate-fade-in-up stagger-3">
              <div className="step-number">03</div>
              <div className="step-icon">
                <ChefHat size={28} />
              </div>
              <h3>Start Cooking!</h3>
              <p>Follow step-by-step instructions to create amazing dishes.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="container">
          <div className="section-header animate-fade-in-up">
            <span className="section-tag">
              <Star size={14} /> Features
            </span>
            <h2 className="section-title">Why Choose ChefAI?</h2>
          </div>

          <div className="features-grid">
            {[
              { icon: <Sparkles size={24} />, title: 'AI-Powered Matching', desc: 'Advanced NLP models understand ingredients and match them to the perfect recipes.' },
              { icon: <Clock size={24} />, title: 'Time-Based Filters', desc: 'Short on time? Filter by cook time to find quick meals that fit your schedule.' },
              { icon: <Heart size={24} />, title: 'Save Favorites', desc: 'Bookmark your favorite recipes and build your personal cookbook.' },
              { icon: <Shield size={24} />, title: 'Dietary Preferences', desc: 'Filter by vegetarian, vegan, gluten-free, and more dietary options.' },
              { icon: <Search size={24} />, title: 'Explore Cuisines', desc: 'Discover recipes from Indian, Italian, Chinese, Mexican, Thai, and 100+ cuisines.' },
              { icon: <ChefHat size={24} />, title: 'Detailed Instructions', desc: 'Step-by-step cooking instructions with complete ingredient lists.' },
            ].map((feature, i) => (
              <div key={i} className={`feature-card animate-fade-in-up stagger-${i + 1}`}>
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-card animate-fade-in-up">
            <div className="cta-glow" />
            <h2>Ready to Transform Your Cooking?</h2>
            <p>Join ChefAI and discover recipes tailored to your pantry.</p>
            <Link to={isAuthenticated ? '/dashboard' : '/register'} className="btn btn-primary btn-lg">
              {isAuthenticated ? 'Open Dashboard' : 'Get Started Free'}
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="container">
          <div className="footer-inner">
            <div className="footer-brand">
              <ChefHat size={20} />
              <span>ChefAI</span>
            </div>
            <p className="footer-text">AI-Powered Recipe Recommendations · Built with ❤️</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
