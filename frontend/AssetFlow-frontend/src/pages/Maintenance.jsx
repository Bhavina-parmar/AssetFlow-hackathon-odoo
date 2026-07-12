import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

const TRANSITIONS = {
  Pending:     ['Approved', 'Rejected'],
  Approved:    ['In Progress'],
  'In Progress': ['Resolved'],
  Resolved:    [],
  Rejected:    [],
};

export default function Maintenance() {
  const { maintenance, addMaintenance, updateMaintenance, assets, currentUser } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ asset: '', assetName: '', issue: '', priority: 'Medium', raised: new Date().toISOString().slice(0, 10) });

  const handleSubmit = (e) => {
    e.preventDefault();
    addMaintenance({ ...form, raisedBy: currentUser?.name });
    setShowForm(false);
    setForm({ asset: '', assetName: '', issue: '', priority: 'Medium', raised: new Date().toISOString().slice(0, 10) });
  };

  const handleAssetChange = (e) => {
    const asset = assets.find((a) => a.tag === e.target.value);
    setForm({ ...form, asset: asset?.tag || '', assetName: asset?.name || '' });
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
            <tr><th>Asset</th><th>Issue</th><th>Priority</th><th>Status</th><th>Assignee</th><th>Raised</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {maintenance.map((m) => (
              <tr key={m.id}>
                <td>
                  <span className="mono asset-tag">{m.asset}</span>
                  <div className="dash-asset-name">{m.assetName}</div>
                </td>
                <td style={{ maxWidth: 200 }}>{m.issue}</td>
                <td>
                  <span className="badge" style={{
                    color: m.priority === 'High' ? 'var(--danger)' : m.priority === 'Medium' ? 'var(--status-reserved)' : 'var(--muted)',
                    background: m.priority === 'High' ? 'var(--danger-soft)' : m.priority === 'Medium' ? 'var(--status-reserved-bg)' : 'var(--surface-sunken)',
                  }}>
                    {m.priority}
                  </span>
                </td>
                <td><StatusBadge status={m.status} /></td>
                <td>{m.assignee || <span style={{ color: 'var(--muted)' }}>Unassigned</span>}</td>
                <td>{m.raised}</td>
                <td>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {TRANSITIONS[m.status]?.map((next) => (
                      <button
                        key={next}
                        className={'btn btn-sm ' + (next === 'Rejected' ? 'btn-danger' : 'btn-secondary')}
                        onClick={() => updateMaintenance(m.id, { status: next })}
                      >
                        {next}
                      </button>
                    ))}
                    {m.status === 'Approved' && !m.assignee && (
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => {
                          const name = prompt('Assign technician name:');
                          if (name) updateMaintenance(m.id, { assignee: name });
                        }}
                      >
                        Assign
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <Modal title="Raise maintenance request" onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit} className="form-stack">
            <div className="field">
              <label>Asset</label>
              <select required value={form.asset} onChange={handleAssetChange}>
                <option value="">Select asset…</option>
                {assets.map((a) => <option key={a.id} value={a.tag}>{a.tag} — {a.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Issue description</label>
              <textarea required value={form.issue} onChange={(e) => setForm({ ...form, issue: e.target.value })} />
            </div>
            <div className="field">
              <label>Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                <option>Low</option><option>Medium</option><option>High</option>
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
