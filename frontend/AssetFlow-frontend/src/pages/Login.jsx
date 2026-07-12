import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import AuthSide from '../components/AuthSide';
import './Auth.css';

export default function Login() {
  const { login } = useApp();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    const result = login(email.trim(), password);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    navigate('/dashboard');
  };

  return (
    <div className="auth-screen">
      <AuthSide />

      <div className="auth-form-side">
        <div className="auth-form-card">
          <h2 className="auth-form-heading">Log in</h2>
          <p className="auth-form-sub">Access your organization's asset workspace.</p>

          {error && <div className="auth-banner">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">Work email</label>
              <input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="button" className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-end', padding: 0, height: 'auto' }}>
              Forgot password?
            </button>
            <button type="submit" className="btn btn-primary">
              Log in
            </button>
          </form>

          <div className="auth-hint-box">
            <strong>Try it:</strong> admin@company.com / admin123 (Admin), or
            kabir.sen@company.com / password (Asset Manager).
          </div>

          <p className="auth-switch">
            New here? <Link to="/signup"><button type="button">Create an employee account</button></Link>
          </p>
        </div>
      </div>
    </div>
  );
}

