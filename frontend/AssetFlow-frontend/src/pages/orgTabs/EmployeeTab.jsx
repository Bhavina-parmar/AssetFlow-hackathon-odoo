import { useMemo, useState } from 'react';
import { useApp } from '../../context/AppContext';
import StatusBadge from '../../components/StatusBadge';

const ROLES = ['Employee', 'Department Head', 'Asset Manager'];

export default function EmployeeTab() {
  const { employees, departments, promoteEmployee, toggleEmployeeStatus } = useApp();
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('All');

  const filtered = useMemo(() => {
    return employees.filter((e) => {
      const matchesSearch =
        !search ||
        e.name.toLowerCase().includes(search.toLowerCase()) ||
        e.email.toLowerCase().includes(search.toLowerCase());
      const matchesDept = deptFilter === 'All' || e.department === deptFilter;
      return matchesSearch && matchesDept;
    });
  }, [employees, search, deptFilter]);

  return (
    <div>
      <div className="panel-toolbar">
        <span className="panel-toolbar-title">
          <strong>{employees.length}</strong> employees · roles are assigned here only
        </span>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <input
            placeholder="Search name or email"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              height: 34,
              padding: '0 10px',
              border: '1px solid var(--line-strong)',
              borderRadius: 'var(--radius-sm)',
              fontSize: 13,
              width: 220,
            }}
          />
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="role-select"
            style={{ height: 34 }}
          >
            <option value="All">All departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>Role</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr className="empty-row">
                <td colSpan={6}>No employees match this search.</td>
              </tr>
            )}
            {filtered.map((e) => (
              <tr key={e.id}>
                <td style={{ fontWeight: 600 }}>{e.name}</td>
                <td style={{ color: 'var(--muted)' }}>{e.email}</td>
                <td>{e.department}</td>
                <td>
                  {e.role === 'Admin' ? (
                    <span className="chip">Admin</span>
                  ) : (
                    <select
                      className="role-select"
                      value={e.role}
                      onChange={async (ev) => {
                        try {
                          await promoteEmployee(e.id, ev.target.value);
                        } catch(err) { console.error(err); }
                      }}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                  )}
                </td>
                <td>
                  <StatusBadge status={e.status} />
                </td>
                <td>
                  <button className="btn btn-ghost btn-sm" onClick={async () => {
                    try {
                      await toggleEmployeeStatus(e.id);
                    } catch(err) { console.error(err); }
                  }}>
                    {e.status === 'Active' ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
