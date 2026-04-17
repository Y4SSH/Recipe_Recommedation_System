import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  ChefHat, Home, Search, Bookmark, BookOpen, User, LogOut,
  Menu, X, Sparkles
} from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  const isLanding = location.pathname === '/' && !isAuthenticated;

  return (
    <nav className={`navbar ${scrolled ? 'navbar-scrolled' : ''} ${isLanding ? 'navbar-transparent' : ''}`}>
      <div className="navbar-inner container">
        <Link to={isAuthenticated ? '/dashboard' : '/'} className="navbar-brand">
          <div className="brand-icon">
            <ChefHat size={24} />
          </div>
          <span className="brand-text">Chef<span className="brand-accent">AI</span></span>
        </Link>

        {isAuthenticated && (
          <div className={`navbar-links ${mobileOpen ? 'navbar-links-open' : ''}`}>
            <Link to="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'nav-link-active' : ''}`}>
              <Home size={18} />
              <span>Home</span>
            </Link>
            <Link to="/explore" className={`nav-link ${isActive('/explore') ? 'nav-link-active' : ''}`}>
              <Search size={18} />
              <span>Explore</span>
            </Link>
            <Link to="/my-recipes" className={`nav-link ${isActive('/my-recipes') ? 'nav-link-active' : ''}`}>
              <BookOpen size={18} />
              <span>My Recipes</span>
            </Link>
            <Link to="/saved" className={`nav-link ${isActive('/saved') ? 'nav-link-active' : ''}`}>
              <Bookmark size={18} />
              <span>Saved</span>
            </Link>
          </div>
        )}

        <div className="navbar-actions">
          {isAuthenticated ? (
            <>
              <Link to="/profile" className={`nav-profile-btn ${isActive('/profile') ? 'nav-link-active' : ''}`}>
                <div className="nav-avatar">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <span className="nav-username">{user?.name?.split(' ')[0] || 'User'}</span>
              </Link>
              <button className="btn btn-ghost nav-logout" onClick={handleLogout} title="Logout">
                <LogOut size={18} />
              </button>
              <button className="navbar-toggle" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </>
          ) : (
            <>
              {location.pathname !== '/login' && (
                <Link to="/login" className="btn btn-ghost">Sign In</Link>
              )}
              {location.pathname !== '/register' && (
                <Link to="/register" className="btn btn-primary btn-sm">
                  <Sparkles size={16} />
                  Get Started
                </Link>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
