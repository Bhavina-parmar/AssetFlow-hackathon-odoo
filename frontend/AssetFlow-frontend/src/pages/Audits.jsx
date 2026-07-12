import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

const ITEM_STATUSES = ['Pending', 'Verified', 'Missing'];

export default function Audits() {
  const { audits, addAudit, updateAuditItem, closeAudit, departments, assets } = useApp();
  const [selected, setSelected] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', department: '', startDate: '' });

  const audit = audits.find((a) => a.id === selected);

  const handleCreate = (e) => {
    e.preventDefault();
    const items = assets
      .filter((a) => a.department === form.department)
      .map((a) => ({ id: `ai${Date.now()}${a.id}`, tag: a.tag, name: a.name, status: 'Pending' }));
    addAudit({ ...form, items });
    setShowForm(false);
    setForm({ name: '', department: '', startDate: '' });
  };

  return (
    <AppLayout title="Audit Cycles" subtitle="Create and manage asset audit cycles by department.">
      {!selected ? (
        <>
          <div className="page-toolbar">
            <span style={{ color: 'var(--muted)', fontSize: 13 }}>{audits.length} cycles</span>
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ New audit cycle</button>
          </div>
          <div className="card">
            <table className="table">
              <thead>
                <tr><th>Name</th><th>Department</th><th>Start date</th><th>Status</th><th>Progress</th><th></th></tr>
              </thead>
              <tbody>
                {audits.map((au) => {
                  const verified = au.items.filter((i) => i.status === 'Verified').length;
                  const pct = au.items.length ? Math.round((verified / au.items.length) * 100) : 0;
                  return (
                    <tr key={au.id}>
                      <td>{au.name}</td>
                      <td>{au.department}</td>
                      <td>{au.startDate}</td>
                      <td><StatusBadge status={au.status} /></td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ flex: 1, height: 6, background: 'var(--line)', borderRadius: 4 }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: 'var(--status-available)', borderRadius: 4 }} />
                          </div>
                          <span className="mono" style={{ fontSize: 11, color: 'var(--muted)' }}>{pct}%</span>
                        </div>
                      </td>
                      <td>
                        <button className="btn btn-ghost btn-sm" onClick={() => setSelected(au.id)}>View</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <>
          <div className="page-toolbar">
            <button className="btn btn-ghost" onClick={() => setSelected(null)}>← Back to audits</button>
            <div style={{ display: 'flex', gap: 8 }}>
              <StatusBadge status={audit.status} />
              {audit.status === 'In Progress' && (
                <button className="btn btn-secondary" onClick={() => { closeAudit(audit.id); setSelected(null); }}>Close audit</button>
              )}
            </div>
          </div>
          <h3 style={{ marginBottom: 16 }}>{audit.name} — {audit.department}</h3>
          <div className="card">
            <table className="table">
              <thead>
                <tr><th>Tag</th><th>Asset name</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {audit.items.map((item) => (
                  <tr key={item.id}>
                    <td><span className="mono asset-tag">{item.tag}</span></td>
                    <td>{item.name}</td>
                    <td><StatusBadge status={item.status} /></td>
                    <td>
                      {audit.status === 'In Progress' && (
                        <div style={{ display: 'flex', gap: 6 }}>
                          {ITEM_STATUSES.filter((s) => s !== item.status).map((s) => (
                            <button key={s} className="btn btn-ghost btn-sm" onClick={() => updateAuditItem(audit.id, item.id, s)}>
                              {s}
                            </button>
                          ))}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showForm && (
        <Modal title="New audit cycle" onClose={() => setShowForm(false)}>
          <form onSubmit={handleCreate} className="form-stack">
            <div className="field">
              <label>Cycle name</label>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Q3 Engineering Floor" />
            </div>
            <div className="field">
              <label>Department</label>
              <select required value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })}>
                <option value="">Select…</option>
                {departments.map((d) => <option key={d.id}>{d.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Start date</label>
              <input type="date" required value={form.startDate} onChange={(e) => setForm({ ...form, startDate: e.target.value })} />
            </div>
            <p style={{ fontSize: 12, color: 'var(--muted)', margin: 0 }}>All assets in the selected department will be added automatically.</p>
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Create</button>
            </div>
          </form>
        </Modal>
      )}
    </AppLayout>
  );
}
