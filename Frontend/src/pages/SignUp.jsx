import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function SignUp() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
   const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signUp } = useAuth();

   const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    const { error: authError } = await signUp(email, password);
    if (authError) {
      setError(authError.message);
    } else {
      setSuccess('Account created! Check your email to confirm, then sign in.');
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
          <h2 className="section-title text-foreground">Create Account</h2>
          <p className="text-sm text-muted-foreground mt-2">Join the premium auction community</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg border border-destructive/30 bg-destructive/5 text-sm text-destructive">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-3 rounded-lg border border-green-500/30 bg-green-500/5 text-sm text-green-400">
            {success}
          </div>
        )}
        
        <form onSubmit={handleSignup} className="flex flex-col gap-4">
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
              minLength={6}
            />
          </div>
           <button type="submit" className="btn-primary mt-2" disabled={loading}>
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>

        <p className="text-sm text-center text-muted-foreground mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:underline font-medium">Sign In</Link>
        </p>
      </div>
    </div>
  );
}
