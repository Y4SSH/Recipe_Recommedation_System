import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import { User, Mail, Calendar, LogOut, ChefHat, Settings, Shield, Locate, Save, Activity } from 'lucide-react';
import './Profile.css';

export default function Profile() {
  const { user, logout, updateProfile } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [diet, setDiet] = useState('');
  const [allergies, setAllergies] = useState('');
  const [locality, setLocality] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.preferences) {
      try {
        const p = JSON.parse(user.preferences);
        setDiet(p.diet || '');
        setAllergies(p.allergies || '');
        setLocality(p.locality || '');
      } catch (e) {
        // silent
      }
    }
  }, [user?.preferences]);

  const handleSavePreferences = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const prefs = JSON.stringify({ diet, allergies, locality });
      await updateProfile({ preferences: prefs });
      toast.success('Preferences saved completely!');
    } catch {
      toast.error('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.info('Logged out successfully');
    navigate('/');
  };

  const joinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    : 'Unknown';

  return (
    <div className="page">
      <div className="container">
        <div className="page-header animate-fade-in-up">
          <h1>Your Profile</h1>
          <p>Manage your account and preferences</p>
        </div>

        <div className="profile-grid">
          <div className="profile-main animate-fade-in-up stagger-1">
            <div className="profile-card glass">
              <div className="profile-avatar-section">
                <div className="profile-avatar-lg">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div>
                  <h2 className="profile-name">{user?.name || 'User'}</h2>
                  <p className="profile-email">{user?.email || 'No email'}</p>
                </div>
              </div>

              <div className="profile-details">
                <div className="profile-detail-item">
                  <User size={18} />
                  <div>
                    <span className="detail-label">Full Name</span>
                    <span className="detail-value">{user?.name || '—'}</span>
                  </div>
                </div>
                <div className="profile-detail-item">
                  <Mail size={18} />
                  <div>
                    <span className="detail-label">Email Address</span>
                    <span className="detail-value">{user?.email || '—'}</span>
                  </div>
                </div>
                <div className="profile-detail-item">
                  <Calendar size={18} />
                  <div>
                    <span className="detail-label">Member Since</span>
                    <span className="detail-value">{joinDate}</span>
                  </div>
                </div>
                <div className="profile-detail-item">
                  <Shield size={18} />
                  <div>
                    <span className="detail-label">Account ID</span>
                    <span className="detail-value detail-mono">{user?.id?.slice(0, 12) || '—'}...</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="profile-card glass profile-customization">
              <div className="profile-card-header">
                <h3><Settings size={20} /> Personal Customizations</h3>
                <p>Help ChefAI understand your specific requirements better</p>
              </div>
              <form onSubmit={handleSavePreferences} className="customization-form">
                <div className="input-group">
                  <label htmlFor="pref-diet"><Activity size={16} /> Dietary Preference</label>
                  <select 
                    id="pref-diet" 
                    className="input-field input-select"
                    value={diet}
                    onChange={(e) => setDiet(e.target.value)}
                  >
                    <option value="">No specific diet (Neutral)</option>
                    <option value="Vegetarian">Vegetarian</option>
                    <option value="Non-Vegetarian">Non-Vegetarian</option>
                    <option value="Vegan">Vegan</option>
                    <option value="Keto">Keto</option>
                  </select>
                </div>

                <div className="input-group">
                  <label htmlFor="pref-allergies"><Shield size={16} /> Allergies & Exclusions</label>
                  <input
                    id="pref-allergies"
                    type="text"
                    className="input-field"
                    placeholder="e.g., Peanuts, Shellfish, Dairy"
                    value={allergies}
                    onChange={(e) => setAllergies(e.target.value)}
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="pref-locality"><Locate size={16} /> Regional Cuisine Preference</label>
                  <input
                    id="pref-locality"
                    type="text"
                    className="input-field"
                    placeholder="e.g., South Indian, Mexican, Continental"
                    value={locality}
                    onChange={(e) => setLocality(e.target.value)}
                  />
                </div>

                <button type="submit" className="btn btn-primary customization-save" disabled={saving}>
                  <Save size={18} /> {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </form>
            </div>
          </div>

          <div className="profile-sidebar animate-fade-in-up stagger-2">
            <div className="profile-actions-card glass">
              <h3><Settings size={18} /> Quick Actions</h3>
              <div className="profile-actions-list">
                <button className="profile-action-item" onClick={() => navigate('/dashboard')}>
                  <ChefHat size={18} />
                  <span>Get Recommendations</span>
                </button>
                <button className="profile-action-item" onClick={() => navigate('/saved')}>
                  <ChefHat size={18} />
                  <span>Saved Recipes</span>
                </button>
                <button className="profile-action-item" onClick={() => navigate('/explore')}>
                  <ChefHat size={18} />
                  <span>Explore Recipes</span>
                </button>
              </div>
            </div>

            <button className="btn btn-danger profile-logout" onClick={handleLogout}>
              <LogOut size={18} /> Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
