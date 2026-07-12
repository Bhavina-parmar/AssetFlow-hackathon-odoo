import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

export default function Allocations() {
  const { allocations, addAllocation, returnAllocation, transfers, addTransfer, updateTransfer, assets, employees, departments } = useApp();
  const [tab, setTab] = useState('allocations');
  const [showAllocForm, setShowAllocForm] = useState(false);
  const [showTransferForm, setShowTransferForm] = useState(false);
  
  // Maps to backend serializer fields: asset (id), employee (id), assigned_date, expected_return_date
  const [aForm, setAForm] = useState({ asset: '', employee: '', assigned_date: '', expected_return_date: '' });
  
  // Transfer request: asset (id), to_employee (user id), reason
  const [tForm, setTForm] = useState({ asset: '', to_employee: '', reason: '' });

  const availableAssets = assets.filter((a) => a.status === 'AVAILABLE');

  const handleAllocSubmit = async (e) => {
    e.preventDefault();
    try {
      await addAllocation(aForm);
      setShowAllocForm(false);
      setAForm({ asset: '', employee: '', assigned_date: '', expected_return_date: '' });
    } catch (err) { console.error(err); }
  };

  const handleTransferSubmit = async (e) => {
    e.preventDefault();
    try {
      await addTransfer({ asset: Number(tForm.asset), to_employee: Number(tForm.to_employee), reason: tForm.reason });
      setShowTransferForm(false);
      setTForm({ asset: '', to_employee: '', reason: '' });
    } catch (err) { console.error(err); }
  };

  const getAssetName = (id) => {
    const a = assets.find(x => x.id === id);
    return a ? a.name : 'Unknown';
  };
  const getAssetTag = (id) => {
    const a = assets.find(x => x.id === id);
    return a ? a.tag : 'Unknown';
  };
  const getEmpName = (id) => {
    const e = employees.find(x => x.id === id);
    return e ? e.name || e.first_name : 'Unknown';
  };
  const getDeptName = (id) => {
    const d = departments.find(x => x.id === id);
    return d ? d.name : 'Unknown';
  };

  return (
    <AppLayout title="Allocation & Transfer" subtitle="Manage asset assignments and transfer requests.">
      <div className="tab-bar">
        <button className={'tab-btn' + (tab === 'allocations' ? ' is-active' : '')} onClick={() => setTab('allocations')}>Allocations</button>
        <button className={'tab-btn' + (tab === 'transfers' ? ' is-active' : '')} onClick={() => setTab('transfers')}>Transfer Requests</button>
      </div>

      {tab === 'allocations' && (
        <>
          <div className="page-toolbar">
            <span style={{ color: 'var(--muted)', fontSize: 13 }}>{allocations.length} records</span>
            <button className="btn btn-primary" onClick={() => setShowAllocForm(true)}>+ Allocate asset</button>
          </div>
          <div className="card">
            <table className="table">
              <thead>
                <tr><th>Asset</th><th>Assigned to</th><th>From date</th><th>To date</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {allocations.map((al) => (
                  <tr key={al.id}>
                    <td><span className="mono asset-tag">{getAssetTag(al.asset)}</span><div className="dash-asset-name">{getAssetName(al.asset)}</div></td>
                    <td>{getEmpName(al.employee)}</td>
                    <td>{al.assigned_date}</td>
                    <td>{al.expected_return_date}</td>
                    <td><StatusBadge status={al.status} /></td>
                    <td>
                      {al.status === 'ACTIVE' && (
                        <button className="btn btn-ghost btn-sm" onClick={async () => {
                          try { await returnAllocation(al.id); } catch(e) { console.error(e); }
                        }}>Mark returned</button>
                      )}
                    </td>
                  </tr>
                ))}
                {allocations.length === 0 && (
                  <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No allocations found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === 'transfers' && (
        <>
          <div className="page-toolbar">
            <span style={{ color: 'var(--muted)', fontSize: 13 }}>{transfers.length} requests</span>
            <button className="btn btn-primary" onClick={() => setShowTransferForm(true)}>+ Request transfer</button>
          </div>
          <div className="card">
            <table className="table">
              <thead>
                <tr><th>Asset</th><th>From</th><th>To</th><th>Reason</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {transfers.map((t) => (
                  <tr key={t.id}>
                    <td><span className="mono asset-tag">{getAssetTag(t.asset)}</span><div className="dash-asset-name">{getAssetName(t.asset)}</div></td>
                    <td>{getEmpName(t.from_employee)}</td>
                    <td>{getEmpName(t.to_employee)}</td>
                    <td>{t.reason}</td>
                    <td><StatusBadge status={t.status} /></td>
                    <td style={{ display: 'flex', gap: 8 }}>
                      {t.status === 'REQUESTED' && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={async () => {
                            try { await updateTransfer(t.id, 'Approved'); } catch(e) { console.error(e); }
                          }}>Approve</button>
                          <button className="btn btn-danger btn-sm" onClick={async () => {
                            try { await updateTransfer(t.id, 'Rejected'); } catch(e) { console.error(e); }
                          }}>Reject</button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
                {transfers.length === 0 && (
                  <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>No transfers found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showAllocForm && (
        <Modal title="Allocate asset" onClose={() => setShowAllocForm(false)}>
          <form onSubmit={handleAllocSubmit} className="form-stack">
            <div className="field">
              <label>Asset</label>
              <select required value={aForm.asset} onChange={(e) => setAForm({ ...aForm, asset: e.target.value })}>
                <option value="">Select available asset…</option>
                {availableAssets.map((a) => <option key={a.id} value={a.id}>{a.tag} — {a.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Assign to</label>
              <select required value={aForm.employee} onChange={(e) => setAForm({ ...aForm, employee: e.target.value })}>
                <option value="">Select employee…</option>
                {employees.filter(e => e.is_active).map((e) => <option key={e.id} value={e.id}>{e.name || e.first_name}</option>)}
              </select>
            </div>

            <div className="field">
              <label>To date</label>
              <input type="date" required value={aForm.expected_return_date} onChange={(e) => setAForm({ ...aForm, expected_return_date: e.target.value })} />
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowAllocForm(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Allocate</button>
            </div>
          </form>
        </Modal>
      )}

      {showTransferForm && (
        <Modal title="Request transfer" onClose={() => setShowTransferForm(false)}>
          <form onSubmit={handleTransferSubmit} className="form-stack">
            <div className="field">
              <label>Asset</label>
              <select required value={tForm.asset} onChange={(e) => setTForm({ ...tForm, asset: e.target.value })}>
                <option value="">Select asset…</option>
                {assets.map((a) => <option key={a.id} value={a.id}>{a.tag} — {a.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Transfer to (employee)</label>
              <select required value={tForm.to_employee} onChange={(e) => setTForm({ ...tForm, to_employee: e.target.value })}>
                <option value="">Select employee…</option>
                {employees.filter(e => e.is_active).map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Reason</label>
              <input value={tForm.reason} onChange={(e) => setTForm({ ...tForm, reason: e.target.value })} placeholder="Why transfer?" />
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowTransferForm(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Submit request</button>
            </div>
          </form>
        </Modal>
      )}
    </AppLayout>
  );
}
