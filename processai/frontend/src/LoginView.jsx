import { useState } from 'react';
import { login, register } from './api';

export default function LoginView({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === 'register') {
        await register(username, password);
        setMode('login');
        return;
      }
      const { access_token } = await login(username, password);
      onLogin(access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function toggleMode() {
    setMode(mode === 'login' ? 'register' : 'login');
    setError(null);
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">ProcessAI</div>
          <div className="login-sub">
            {mode === 'login' ? 'Sign in to your account' : 'Create account'}
          </div>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-field-group">
            <label className="login-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="field"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="login-field-group">
            <label className="login-label" htmlFor="password">Password</label>
            <input
              id="password"
              className="field"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="form-error">{error}</div>}
          <button className="btn btn-primary btn-full btn-lg" type="submit" disabled={loading}>
            {loading ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>
        <button className="link-btn" onClick={toggleMode}>
          {mode === 'login' ? 'Need an account? Register' : 'Have an account? Sign in'}
        </button>
      </div>
    </div>
  );
}
