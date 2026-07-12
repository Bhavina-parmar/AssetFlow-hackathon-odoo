import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

export default function Bookings() {
  const { bookings, addBooking, cancelBooking, assets, currentUser, employees } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [conflict, setConflict] = useState('');
  const [form, setForm] = useState({ resource: '', date: '', from: '', to: '' });

  const bookableAssets = assets.filter((a) => ['AVAILABLE', 'ALLOCATED'].includes(a.status));

  const getAssetName = (id) => assets.find(a => a.id === id)?.name || 'Unknown';
  const getAssetTag = (id) => assets.find(a => a.id === id)?.tag || 'Unknown';
  const getEmpName = (id) => {
    const e = employees.find(x => x.id === id);
    return e ? e.name || e.first_name : 'Unknown';
  };

  const checkConflict = (resourceId, date, from, to) => {
    return bookings.some(
      (b) => {
        if (b.resource !== Number(resourceId)) return false;
        if (b.status === 'CANCELLED' || b.status === 'COMPLETED') return false;
        const bDate = b.start_time.split('T')[0];
        if (bDate !== date) return false;
        const bFrom = b.start_time.split('T')[1].slice(0, 5);
        const bTo = b.end_time.split('T')[1].slice(0, 5);
        return from < bTo && to > bFrom;
      }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (checkConflict(form.resource, form.date, form.from, form.to)) {
      setConflict('This resource is already booked for the selected time slot. Please choose a different time.');
      return;
    }
    
    // Combine date and time
    const start_time = `${form.date}T${form.from}:00Z`; // Using UTC for simplicity, or handle local time
    const end_time = `${form.date}T${form.to}:00Z`;

    try {
      await addBooking({ resource: Number(form.resource), start_time, end_time });
      setShowForm(false);
      setConflict('');
      setForm({ resource: '', date: '', from: '', to: '' });
    } catch(err) {
      console.error(err);
      setConflict('Failed to book. ' + (err.error || ''));
    }
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
            {bookings.map((b) => {
              const dt = b.start_time.split('T');
              const date = dt[0];
              const from = dt[1].slice(0, 5);
              const to = b.end_time.split('T')[1].slice(0, 5);
              
              return (
                <tr key={b.id}>
                  <td>
                    <span className="mono asset-tag">{getAssetTag(b.resource)}</span>
                    <div className="dash-asset-name">{getAssetName(b.resource)}</div>
                  </td>
                  <td>{getEmpName(b.booked_by)}</td>
                  <td>{date}</td>
                  <td className="mono">{from} – {to}</td>
                  <td><StatusBadge status={b.status} /></td>
                  <td>
                    {b.status === 'UPCOMING' && (
                      <button className="btn btn-danger btn-sm" onClick={async () => {
                        try { await cancelBooking(b.id); } catch(e) { console.error(e); }
                      }}>Cancel</button>
                    )}
                  </td>
                </tr>
              );
            })}
            {bookings.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No bookings found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <Modal title="Book a resource" onClose={() => { setShowForm(false); setConflict(''); }}>
          <form onSubmit={handleSubmit} className="form-stack">
            <div className="field">
              <label>Resource</label>
              <select required value={form.resource} onChange={(e) => {
                setForm({ ...form, resource: e.target.value });
                setConflict('');
              }}>
                <option value="">Select resource…</option>
                {bookableAssets.map((a) => <option key={a.id} value={a.id}>{a.tag} — {a.name}</option>)}
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
