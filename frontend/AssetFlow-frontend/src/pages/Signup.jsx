import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import AuthSide from '../components/AuthSide';
import './Auth.css';

export default function Signup() {
  const { signup, departments } = useApp();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [department, setDepartment] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }

    const result = await signup({ name: name.trim(), email: email.trim(), password, department });
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
          <h2 className="auth-form-heading">Create your account</h2>
          <p className="auth-form-sub">
            Signup creates an Employee account. Admins grant Department Head or
            Asset Manager access later from the Employee Directory.
          </p>

          {error && <div className="auth-banner">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="name">Full name</label>
              <input
                id="name"
                type="text"
                placeholder="Jordan Blake"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="signup-email">Work email</label>
              <input
                id="signup-email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="department">Department (optional)</label>
              <select
                id="department"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
              >
                <option value="">Not sure yet</option>
                {departments
                  .filter((d) => d.status === 'Active')
                  .map((d) => (
                    <option key={d.id} value={d.name}>
                      {d.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="signup-password">Password</label>
              <input
                id="signup-password"
                type="password"
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="confirm-password">Confirm password</label>
              <input
                id="confirm-password"
                type="password"
                placeholder="Repeat your password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Create account
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/login"><button type="button">Log in</button></Link>
          </p>
        </div>
      </div>
    </div>
  );
}
