import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const NAV_SECTIONS = [
  {
    label: 'Overview',
    items: [{ to: '/dashboard', label: 'Dashboard', glyph: '◱' }],
  },
  {
    label: 'Setup',
    items: [{ to: '/org-setup', label: 'Organization Setup', glyph: '⚙' }],
  },
  {
    label: 'Operations',
    items: [
      { to: '/assets',      label: 'Asset Registry',       glyph: '▤' },
      { to: '/allocations', label: 'Allocation & Transfer', glyph: '⇄' },
      { to: '/bookings',    label: 'Resource Booking',      glyph: '▦' },
      { to: '/maintenance', label: 'Maintenance',           glyph: '✎' },
      { to: '/audits',      label: 'Audit Cycles',          glyph: '✓' },
    ],
  },
  {
    label: 'Insight',
    items: [
      { to: '/reports',  label: 'Reports & Analytics',      glyph: '▲' },
      { to: '/activity', label: 'Activity & Notifications',  glyph: '●' },
    ],
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-brand-mark">AF</span>
        <span className="sidebar-brand-name">AssetFlow</span>
      </div>

      <nav className="sidebar-nav">
        {NAV_SECTIONS.map((section) => (
          <div className="sidebar-section" key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            {section.items.map((item) => (
              <NavLink
                to={item.to}
                key={item.to}
                className={({ isActive }) => 'sidebar-link' + (isActive ? ' is-active' : '')}
              >
                <span className="sidebar-glyph">{item.glyph}</span>
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="mono">v1.0 — AssetFlow</span>
      </div>
    </aside>
  );
}
