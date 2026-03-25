import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { User, Mail, Lock, Eye, EyeOff, ChefHat, ArrowRight } from 'lucide-react';
import './Auth.css';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPass, setConfirmPass] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { register, login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const validate = () => {
    const e = {};
    if (!name.trim()) e.name = 'Name is required';
    if (!email) e.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Invalid email address';
    if (!password) e.password = 'Password is required';
    else if (password.length < 6) e.password = 'Password must be at least 6 characters';
    if (password !== confirmPass) e.confirmPass = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await register(name, email, password);
      await login(email, password);
      toast.success('Account created! Welcome to ChefAI 🎉');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg">
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
      </div>
      <div className="auth-container animate-fade-in-up">
        <div className="auth-card glass">
          <div className="auth-header">
            <div className="auth-logo">
              <ChefHat size={28} />
            </div>
            <h1>Create Account</h1>
            <p>Join ChefAI and start discovering recipes</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="input-group">
              <label htmlFor="reg-name">Full Name</label>
              <div className="input-icon-wrapper">
                <User size={18} className="input-icon" />
                <input
                  id="reg-name"
                  type="text"
                  className={`input-field input-with-icon ${errors.name ? 'input-error' : ''}`}
                  placeholder="Your full name"
                  value={name}
                  onChange={e => { setName(e.target.value); setErrors(p => ({ ...p, name: '' })); }}
                />
              </div>
              {errors.name && <span className="error-text">{errors.name}</span>}
            </div>

            <div className="input-group">
              <label htmlFor="reg-email">Email</label>
              <div className="input-icon-wrapper">
                <Mail size={18} className="input-icon" />
                <input
                  id="reg-email"
                  type="email"
                  className={`input-field input-with-icon ${errors.email ? 'input-error' : ''}`}
                  placeholder="you@example.com"
                  value={email}
                  onChange={e => { setEmail(e.target.value); setErrors(p => ({ ...p, email: '' })); }}
                />
              </div>
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="input-group">
              <label htmlFor="reg-password">Password</label>
              <div className="input-icon-wrapper">
                <Lock size={18} className="input-icon" />
                <input
                  id="reg-password"
                  type={showPass ? 'text' : 'password'}
                  className={`input-field input-with-icon ${errors.password ? 'input-error' : ''}`}
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={e => { setPassword(e.target.value); setErrors(p => ({ ...p, password: '' })); }}
                />
                <button type="button" className="input-toggle" onClick={() => setShowPass(!showPass)}>
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <div className="input-group">
              <label htmlFor="reg-confirm">Confirm Password</label>
              <div className="input-icon-wrapper">
                <Lock size={18} className="input-icon" />
                <input
                  id="reg-confirm"
                  type={showPass ? 'text' : 'password'}
                  className={`input-field input-with-icon ${errors.confirmPass ? 'input-error' : ''}`}
                  placeholder="Repeat your password"
                  value={confirmPass}
                  onChange={e => { setConfirmPass(e.target.value); setErrors(p => ({ ...p, confirmPass: '' })); }}
                />
              </div>
              {errors.confirmPass && <span className="error-text">{errors.confirmPass}</span>}
            </div>

            <button type="submit" className="btn btn-primary btn-lg auth-submit" disabled={loading}>
              {loading ? (
                <span className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
              ) : (
                <>Create Account <ArrowRight size={18} /></>
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p>Already have an account? <Link to="/login" className="auth-link">Sign in</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}
