import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

export default function Bookings() {
  const { bookings, addBooking, cancelBooking, assets, currentUser } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [conflict, setConflict] = useState('');
  const [form, setForm] = useState({ resource: '', resourceTag: '', date: '', from: '', to: '' });

  const bookableAssets = assets.filter((a) => ['Available', 'Allocated'].includes(a.status));

  const checkConflict = (tag, date, from, to) => {
    return bookings.some(
      (b) =>
        b.resourceTag === tag &&
        b.date === date &&
        b.status !== 'Cancelled' &&
        b.status !== 'Completed' &&
        from < b.to &&
        to > b.from
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (checkConflict(form.resourceTag, form.date, form.from, form.to)) {
      setConflict('This resource is already booked for the selected time slot. Please choose a different time.');
      return;
    }
    addBooking({ ...form, bookedBy: currentUser?.name || 'Unknown' });
    setShowForm(false);
    setConflict('');
    setForm({ resource: '', resourceTag: '', date: '', from: '', to: '' });
  };

  const handleAssetChange = (e) => {
    const asset = bookableAssets.find((a) => a.tag === e.target.value);
    setForm({ ...form, resourceTag: asset?.tag || '', resource: asset?.name || '' });
    setConflict('');
  };

  return (
    <AppLayout title="Resource Booking" subtitle="Book shared resources and view upcoming slots.">
      <div className="page-toolbar">
        <span style={{ color: 'var(--muted)', fontSize: 13 }}>{bookings.length} bookings</span>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ Book resource</button>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr><th>Resource</th><th>Booked by</th><th>Date</th><th>Slot</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {bookings.map((b) => (
              <tr key={b.id}>
                <td>
                  <span className="mono asset-tag">{b.resourceTag}</span>
                  <div className="dash-asset-name">{b.resource}</div>
                </td>
                <td>{b.bookedBy}</td>
                <td>{b.date}</td>
                <td className="mono">{b.from} – {b.to}</td>
                <td><StatusBadge status={b.status} /></td>
                <td>
                  {b.status === 'Upcoming' && (
                    <button className="btn btn-danger btn-sm" onClick={() => cancelBooking(b.id)}>Cancel</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <Modal title="Book a resource" onClose={() => { setShowForm(false); setConflict(''); }}>
          <form onSubmit={handleSubmit} className="form-stack">
            <div className="field">
              <label>Resource</label>
              <select required value={form.resourceTag} onChange={handleAssetChange}>
                <option value="">Select resource…</option>
                {bookableAssets.map((a) => <option key={a.id} value={a.tag}>{a.tag} — {a.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Date</label>
              <input type="date" required value={form.date} onChange={(e) => { setForm({ ...form, date: e.target.value }); setConflict(''); }} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="field">
                <label>From</label>
                <input type="time" required value={form.from} onChange={(e) => { setForm({ ...form, from: e.target.value }); setConflict(''); }} />
              </div>
              <div className="field">
                <label>To</label>
                <input type="time" required value={form.to} onChange={(e) => { setForm({ ...form, to: e.target.value }); setConflict(''); }} />
              </div>
            </div>
            {conflict && <p style={{ color: 'var(--danger)', fontSize: 13, margin: 0 }}>⚠ {conflict}</p>}
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => { setShowForm(false); setConflict(''); }}>Cancel</button>
              <button type="submit" className="btn btn-primary">Book</button>
            </div>
          </form>
        </Modal>
      )}
    </AppLayout>
  );
}
