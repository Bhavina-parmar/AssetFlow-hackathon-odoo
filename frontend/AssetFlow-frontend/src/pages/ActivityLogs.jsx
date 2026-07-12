import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import { useApp } from '../context/AppContext';

const ACTION_STYLE = {
  ALLOCATE:    { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  BOOK:        { color: 'var(--status-reserved)',    bg: 'var(--status-reserved-bg)'    },
  TRANSFER:    { color: 'var(--accent)',             bg: 'var(--accent-soft)'            },
  MAINTENANCE: { color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
  OVERDUE:     { color: 'var(--danger)',             bg: 'var(--danger-soft)'            },
  CREATE:      { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
  CANCEL:      { color: 'var(--muted)',              bg: 'var(--surface-sunken)'         },
  AUDIT:       { color: 'var(--ink-soft)',           bg: 'var(--surface-sunken)'         },
  VERIFY:      { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
};

const MODULES = ['All', 'Allocation', 'Booking', 'Transfer', 'Maintenance', 'Asset', 'Audit'];

export default function ActivityLogs() {
  const { logs } = useApp();
  const [filterModule, setFilterModule] = useState('All');
  const [search, setSearch] = useState('');

  const filtered = logs.filter((l) => {
    const q = search.toLowerCase();
    return (
      (filterModule === 'All' || l.module === filterModule) &&
      (!q || l.detail.toLowerCase().includes(q) || l.user.toLowerCase().includes(q) || l.target.toLowerCase().includes(q))
    );
  });

  return (
    <AppLayout title="Activity & Notifications" subtitle="Full audit trail of all actions across the system.">
      <div className="page-toolbar">
        <input
          className="search-input"
          placeholder="Search by user, asset, or detail…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="filter-select" value={filterModule} onChange={(e) => setFilterModule(e.target.value)}>
          {MODULES.map((m) => <option key={m}>{m}</option>)}
        </select>
        <span style={{ color: 'var(--muted)', fontSize: 13 }}>{filtered.length} entries</span>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr><th>Time</th><th>User</th><th>Action</th><th>Target</th><th>Detail</th><th>Module</th></tr>
          </thead>
          <tbody>
            {filtered.map((l) => {
              const s = ACTION_STYLE[l.action] || { color: 'var(--muted)', bg: 'var(--surface-sunken)' };
              return (
                <tr key={l.id}>
                  <td className="mono" style={{ fontSize: 12, color: 'var(--muted)', whiteSpace: 'nowrap' }}>{l.time}</td>
                  <td>{l.user}</td>
                  <td>
                    <span className="badge" style={{ color: s.color, background: s.bg }}>{l.action}</span>
                  </td>
                  <td><span className="mono asset-tag">{l.target}</span></td>
                  <td style={{ color: 'var(--ink-soft)' }}>{l.detail}</td>
                  <td style={{ color: 'var(--muted)', fontSize: 12 }}>{l.module}</td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: 32 }}>No logs found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
