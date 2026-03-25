import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import { User, Mail, Calendar, LogOut, ChefHat, Settings, Shield } from 'lucide-react';
import './Profile.css';

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

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
