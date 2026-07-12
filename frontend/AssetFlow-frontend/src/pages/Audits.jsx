import { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';
import { api } from '../api';

const ITEM_STATUSES = ['PENDING', 'VERIFIED', 'MISSING'];

export default function Audits() {
  const { audits, addAudit, closeAudit, departments, assets } = useApp();
  const [selected, setSelected] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ scope_department: '', start_date: '' });
  const [items, setItems] = useState([]);

  const audit = audits.find((a) => a.id === selected);

  useEffect(() => {
    if (selected) {
      api.audits.listItems(selected).then(data => setItems(data || []));
    }
  }, [selected]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await addAudit({ ...form, scope_department: Number(form.scope_department) });
      setShowForm(false);
      setForm({ scope_department: '', start_date: '' });
    } catch(err) { console.error(err); }
  };

  const handleUpdateItem = async (itemId, status) => {
    try {
      await api.audits.markItem(itemId, status);
      const data = await api.audits.listItems(selected);
      setItems(data || []);
    } catch(err) { console.error(err); }
  };

  const getDeptName = (id) => departments.find(d => d.id === id)?.name || 'All';
  const getAssetName = (id) => assets.find(a => a.id === id)?.name || 'Unknown';
  const getAssetTag = (id) => assets.find(a => a.id === id)?.tag || 'Unknown';

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
                <tr><th>Department</th><th>Start date</th><th>End date</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {audits.map((au) => (
                  <tr key={au.id}>
                    <td>{getDeptName(au.scope_department)}</td>
                    <td>{au.start_date}</td>
                    <td>{au.end_date || '—'}</td>
                    <td><StatusBadge status={au.status} /></td>
                    <td>
                      <button className="btn btn-ghost btn-sm" onClick={() => setSelected(au.id)}>View</button>
                    </td>
                  </tr>
                ))}
                {audits.length === 0 && (
                  <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No audits found.</td></tr>
                )}
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
              {audit.status === 'IN_PROGRESS' && (
                <button className="btn btn-secondary" onClick={async () => { 
                  try { await closeAudit(audit.id); setSelected(null); } catch(e) { console.error(e); }
                }}>Close audit</button>
              )}
            </div>
          </div>
          <h3 style={{ marginBottom: 16 }}>Audit — {getDeptName(audit.scope_department)}</h3>
          <div className="card">
            <table className="table">
              <thead>
                <tr><th>Tag</th><th>Asset name</th><th>Result</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td><span className="mono asset-tag">{getAssetTag(item.asset)}</span></td>
                    <td>{getAssetName(item.asset)}</td>
                    <td><StatusBadge status={item.result} /></td>
                    <td>
                      {audit.status === 'IN_PROGRESS' && (
                        <div style={{ display: 'flex', gap: 6 }}>
                          {ITEM_STATUSES.filter((s) => s !== item.result).map((s) => (
                            <button key={s} className="btn btn-ghost btn-sm" onClick={() => handleUpdateItem(item.id, s)}>
                              {s}
                            </button>
                          ))}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
                {items.length === 0 && (
                  <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No items in this audit.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showForm && (
        <Modal title="New audit cycle" onClose={() => setShowForm(false)}>
          <form onSubmit={handleCreate} className="form-stack">
            <div className="field">
              <label>Department</label>
              <select required value={form.scope_department} onChange={(e) => setForm({ ...form, scope_department: e.target.value })}>
                <option value="">Select…</option>
                {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Start date</label>
              <input type="date" required value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
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
