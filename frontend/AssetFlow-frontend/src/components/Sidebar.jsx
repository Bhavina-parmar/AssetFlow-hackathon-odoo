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
      { to: '/assets', label: 'Asset Registry', glyph: '▤', disabled: true },
      { to: '/allocations', label: 'Allocation & Transfer', glyph: '⇄', disabled: true },
      { to: '/bookings', label: 'Resource Booking', glyph: '▦', disabled: true },
      { to: '/maintenance', label: 'Maintenance', glyph: '✎', disabled: true },
      { to: '/audits', label: 'Audit Cycles', glyph: '✓', disabled: true },
    ],
  },
  {
    label: 'Insight',
    items: [
      { to: '/reports', label: 'Reports & Analytics', glyph: '▲', disabled: true },
      { to: '/activity', label: 'Activity & Notifications', glyph: '●', disabled: true },
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
            {section.items.map((item) =>
              item.disabled ? (
                <span className="sidebar-link is-disabled" key={item.to} title="Coming soon">
                  <span className="sidebar-glyph">{item.glyph}</span>
                  {item.label}
                </span>
              ) : (
                <NavLink
                  to={item.to}
                  key={item.to}
                  className={({ isActive }) =>
                    'sidebar-link' + (isActive ? ' is-active' : '')
                  }
                >
                  <span className="sidebar-glyph">{item.glyph}</span>
                  {item.label}
                </NavLink>
              )
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="mono">v0.1 — mock data</span>
      </div>
    </aside>
  );
}
