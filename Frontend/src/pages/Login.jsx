import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';


export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signIn } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const { error: authError } = await signIn(email, password);
    if (authError) {
      setError(authError.message);
    } else {
      navigate('/');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 pt-16">
      <div className="glass-card gold-glow p-8 w-full max-w-md opacity-0 animate-fade-up">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl gold-gradient mx-auto mb-4 flex items-center justify-center">
            <span className="text-lg font-bold" style={{ color: 'hsl(220, 20%, 6%)' }}>AB</span>
          </div>
          <h2 className="section-title text-foreground">Welcome Back</h2>
          <p className="text-sm text-muted-foreground mt-2">Sign in to your account</p>
        </div>
        
        {error && <div className="alert alert-error mb-4">{error}</div>}{error && (
          <div className="mb-4 p-3 rounded-lg border border-destructive/30 bg-destructive/5 text-sm text-destructive">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn-primary mt-2" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-sm text-center text-muted-foreground mt-6">
          New here?{' '}
          <Link to="/signup" className="text-primary hover:underline font-medium">Create Account</Link>
        </p>
      </div>
    </div>
  );
}
