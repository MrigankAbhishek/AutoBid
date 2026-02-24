import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';


export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const isActive = (path) => location.pathname === path;

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-t-0 border-x-0 rounded-none">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg gold-gradient flex items-center justify-center">
            <span className="text-sm font-bold" style={{ color: 'hsl(220, 20%, 6%)' }}>AB</span>
          </div>
          <span className="text-lg font-bold font-display gold-text">AutoBid</span>
        </Link>

        <div className="flex items-center gap-1">
          {[
            { path: '/', label: 'Auctions' },
            { path: '/sell', label: 'Sell' },
          ].map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive(path)
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
              }`}
            >
              {label}
            </Link>
          ))}
          <div className="w-px h-6 bg-border mx-2" />
          {user ? (
            <button onClick={handleSignOut} className="btn-outline text-sm !px-4 !py-2">
              Logout
            </button>
          ) : (
            <Link to="/login" className="btn-outline text-sm !px-4 !py-2">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
