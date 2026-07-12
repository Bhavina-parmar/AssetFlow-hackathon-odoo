import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import './Topbar.css';

export default function Topbar({ title, subtitle }) {
  const { currentUser, logout } = useApp();
  const navigate = useNavigate();

  const initials = (currentUser?.name || '?')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="topbar">
      <div>
        <h1 className="topbar-title">{title}</h1>
        {subtitle && <p className="topbar-subtitle">{subtitle}</p>}
      </div>

      <div className="topbar-user">
        <div className="topbar-user-info">
          <span className="topbar-user-name">{currentUser?.name}</span>
          <span className="topbar-user-role">{currentUser?.role}</span>
        </div>
        <div className="topbar-avatar">{initials}</div>
        <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
          Log out
        </button>
      </div>
    </header>
  );
}
