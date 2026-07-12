import { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import { api } from '../api';

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

const MODULES = ['All', 'Allocation', 'Booking', 'TransferRequest', 'MaintenanceRequest', 'Asset', 'AuditCycle'];

export default function ActivityLogs() {
  const [logs, setLogs] = useState([]);
  const [filterModule, setFilterModule] = useState('All');
  const [search, setSearch] = useState('');

  useEffect(() => {
    let active = true;
    async function fetchLogs() {
      try {
        const params = {};
        if (filterModule !== 'All') params.module = filterModule;
        if (search) params.search = search;
        const data = await api.logs.list(params);
        if (active) setLogs(data || []);
      } catch(err) {
        console.error(err);
      }
    }
    fetchLogs();
    return () => { active = false; };
  }, [filterModule, search]);

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
          {MODULES.map((m) => <option key={m} value={m}>{m === 'All' ? 'All modules' : m}</option>)}
        </select>
        <span style={{ color: 'var(--muted)', fontSize: 13 }}>{logs.length} entries</span>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr><th>Time</th><th>User</th><th>Action</th><th>Target type</th><th>Detail</th></tr>
          </thead>
          <tbody>
            {logs.map((l) => {
              const s = ACTION_STYLE[l.action.toUpperCase()] || { color: 'var(--muted)', bg: 'var(--surface-sunken)' };
              return (
                <tr key={l.id}>
                  <td className="mono" style={{ fontSize: 12, color: 'var(--muted)', whiteSpace: 'nowrap' }}>{new Date(l.timestamp).toLocaleString()}</td>
                  <td>{l.actor?.username || 'System'}</td>
                  <td>
                    <span className="badge" style={{ color: s.color, background: s.bg }}>{l.action}</span>
                  </td>
                  <td><span className="mono asset-tag">{l.target_type} {l.target_id}</span></td>
                  <td style={{ color: 'var(--ink-soft)' }}>{l.meta?.description || l.action}</td>
                </tr>
              );
            })}
            {logs.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--muted)', padding: 32 }}>No logs found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
