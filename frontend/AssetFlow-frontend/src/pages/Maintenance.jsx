import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

const TRANSITIONS = {
  PENDING:     ['Approved', 'Rejected'],
  APPROVED:    ['In Progress'],
  IN_PROGRESS: ['Resolved'],
  RESOLVED:    [],
  REJECTED:    [],
};

export default function Maintenance() {
  const { maintenance, addMaintenance, updateMaintenance, assets, employees } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ asset: '', issue_text: '', priority: 'MEDIUM' });

  const getAssetName = (id) => assets.find(a => a.id === id)?.name || 'Unknown';
  const getAssetTag = (id) => assets.find(a => a.id === id)?.tag || 'Unknown';
  const getEmpName = (id) => {
    if (!id) return null;
    const e = employees.find(x => x.id === id);
    return e ? e.name || e.first_name : 'Unknown';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await addMaintenance({ ...form, asset: Number(form.asset) });
      setShowForm(false);
      setForm({ asset: '', issue_text: '', priority: 'MEDIUM' });
    } catch(err) { console.error(err); }
  };

  return (
    <AppLayout title="Maintenance" subtitle="Raise and track maintenance requests through their lifecycle.">
      <div className="page-toolbar">
        <span style={{ color: 'var(--muted)', fontSize: 13 }}>{maintenance.length} requests</span>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ Raise request</button>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr><th>Asset</th><th>Issue</th><th>Priority</th><th>Status</th><th>Assignee</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {maintenance.map((m) => (
              <tr key={m.id}>
                <td>
                  <span className="mono asset-tag">{getAssetTag(m.asset)}</span>
                  <div className="dash-asset-name">{getAssetName(m.asset)}</div>
                </td>
                <td style={{ maxWidth: 200 }}>{m.issue_text}</td>
                <td>
                  <span className="badge" style={{
                    color: m.priority === 'HIGH' ? 'var(--danger)' : m.priority === 'MEDIUM' ? 'var(--status-reserved)' : 'var(--muted)',
                    background: m.priority === 'HIGH' ? 'var(--danger-soft)' : m.priority === 'MEDIUM' ? 'var(--status-reserved-bg)' : 'var(--surface-sunken)',
                  }}>
                    {m.priority}
                  </span>
                </td>
                <td><StatusBadge status={m.status} /></td>
                <td>{getEmpName(m.technician) || <span style={{ color: 'var(--muted)' }}>Unassigned</span>}</td>
                <td>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {TRANSITIONS[m.status]?.map((next) => (
                      <button
                        key={next}
                        className={'btn btn-sm ' + (next === 'Rejected' ? 'btn-danger' : 'btn-secondary')}
                        onClick={async () => {
                          try { await updateMaintenance(m.id, { status: next }); } catch(e) { console.error(e); }
                        }}
                      >
                        {next}
                      </button>
                    ))}
                    {m.status === 'APPROVED' && !m.technician && (
                      <select
                        className="btn btn-sm btn-ghost"
                        value=""
                        onChange={async (e) => {
                          if (!e.target.value) return;
                          try { await updateMaintenance(m.id, { assignee: Number(e.target.value) }); } catch(err) { console.error(err); }
                        }}
                      >
                        <option value="">Assign...</option>
                        {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name || emp.first_name}</option>)}
                      </select>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {maintenance.length === 0 && (
              <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No maintenance requests found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <Modal title="Raise maintenance request" onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit} className="form-stack">
            <div className="field">
              <label>Asset</label>
              <select required value={form.asset} onChange={(e) => setForm({...form, asset: e.target.value})}>
                <option value="">Select asset…</option>
                {assets.map((a) => <option key={a.id} value={a.id}>{a.tag} — {a.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Issue description</label>
              <textarea required value={form.issue_text} onChange={(e) => setForm({ ...form, issue_text: e.target.value })} />
            </div>
            <div className="field">
              <label>Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                <option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option>
              </select>
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Submit</button>
            </div>
          </form>
        </Modal>
      )}
    </AppLayout>
  );
}
