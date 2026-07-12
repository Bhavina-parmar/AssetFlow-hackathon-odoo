import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

const STATUSES = ['AVAILABLE', 'ALLOCATED', 'RESERVED', 'UNDER_MAINTENANCE', 'LOST', 'RETIRED', 'DISPOSED'];

export default function Assets() {
  const { assets, addAsset, updateAsset, categories, departments } = useApp();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', category: '', department: '', acquisition_date: '', acquisition_cost: '' });

  const getCategoryName = (id) => categories.find(c => c.id === id)?.name || '—';
  const getDeptName = (id) => departments.find(d => d.id === id)?.name || '—';

  const filtered = assets.filter((a) => {
    const q = search.toLowerCase();
    return (
      (!filterStatus || a.status === filterStatus) &&
      (!q || a.name?.toLowerCase().includes(q) || a.tag?.toLowerCase().includes(q))
    );
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await addAsset({ ...form, acquisition_cost: Number(form.acquisition_cost) });
      setShowForm(false);
      setForm({ name: '', category: '', department: '', acquisition_date: '', acquisition_cost: '' });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <AppLayout title="Asset Registry" subtitle="All registered assets and their current status.">
      <div className="page-toolbar">
        <input
          className="search-input"
          placeholder="Search by name or tag…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="filter-select" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ Register asset</button>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Tag</th><th>Name</th><th>Category</th><th>Department</th><th>Status</th><th>Purchase date</th><th>Value (₹)</th><th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((a) => (
              <tr key={a.id}>
                <td><span className="mono asset-tag">{a.tag}</span></td>
                <td>{a.name}</td>
                <td>{getCategoryName(a.category)}</td>
                <td>{getDeptName(a.department)}</td>
                <td><StatusBadge status={a.status || 'AVAILABLE'} /></td>
                <td>{a.acquisition_date}</td>
                <td className="mono">{a.acquisition_cost ? Number(a.acquisition_cost).toLocaleString('en-IN') : '—'}</td>
                <td>
                  <select
                    className="filter-select"
                    value={a.status || 'AVAILABLE'}
                    onChange={async (e) => {
                      try {
                        await updateAsset(a.id, { status: e.target.value });
                      } catch(err) { console.error(err); }
                    }}
                  >
                    {STATUSES.map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                  </select>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No assets found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <Modal title="Register new asset" onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit} className="form-stack">
            <div className="field">
              <label>Asset name</label>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="field">
              <label>Category</label>
              <select required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                <option value="">Select…</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Department</label>
              <select required value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })}>
                <option value="">Select…</option>
                {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Purchase date</label>
              <input type="date" required value={form.acquisition_date} onChange={(e) => setForm({ ...form, acquisition_date: e.target.value })} />
            </div>
            <div className="field">
              <label>Value (₹)</label>
              <input type="number" min="0" value={form.acquisition_cost} onChange={(e) => setForm({ ...form, acquisition_cost: e.target.value })} />
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Register</button>
            </div>
          </form>
        </Modal>
      )}
    </AppLayout>
  );
}
