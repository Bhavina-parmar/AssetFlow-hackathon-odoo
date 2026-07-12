import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../context/AppContext';

export default function Allocations() {
  const { allocations, addAllocation, returnAllocation, transfers, addTransfer, updateTransfer, assets, employees } = useApp();
  const [tab, setTab] = useState('allocations');
  const [showAllocForm, setShowAllocForm] = useState(false);
  const [showTransferForm, setShowTransferForm] = useState(false);
  const [aForm, setAForm] = useState({ asset: '', assignedTo: '', department: '', from: '', to: '' });
  const [tForm, setTForm] = useState({ asset: '', assetName: '', from: '', to: '', requestedBy: '' });

  const availableAssets = assets.filter((a) => a.status === 'Available');

  const handleAllocSubmit = (e) => {
    e.preventDefault();
    addAllocation(aForm);
    setShowAllocForm(false);
    setAForm({ asset: '', assignedTo: '', department: '', from: '', to: '' });
  };

  const handleTransferSubmit = (e) => {
    e.preventDefault();
    addTransfer(tForm);
    setShowTransferForm(false);
    setTForm({ asset: '', assetName: '', from: '', to: '', requestedBy: '' });
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
                <tr><th>Asset</th><th>Assigned to</th><th>Department</th><th>From</th><th>To</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {allocations.map((al) => (
                  <tr key={al.id}>
                    <td><span className="mono asset-tag">{al.asset}</span><div className="dash-asset-name">{al.assetName}</div></td>
                    <td>{al.assignedTo}</td>
                    <td>{al.department}</td>
                    <td>{al.from}</td>
                    <td>{al.to}</td>
                    <td><StatusBadge status={al.status} /></td>
                    <td>
                      {al.status === 'Active' && (
                        <button className="btn btn-ghost btn-sm" onClick={() => returnAllocation(al.id)}>Mark returned</button>
                      )}
                    </td>
                  </tr>
                ))}
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
                <tr><th>Asset</th><th>From</th><th>To</th><th>Requested by</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {transfers.map((t) => (
                  <tr key={t.id}>
                    <td><span className="mono asset-tag">{t.asset}</span><div className="dash-asset-name">{t.assetName}</div></td>
                    <td>{t.from}</td>
                    <td>{t.to}</td>
                    <td>{t.requestedBy}</td>
                    <td><StatusBadge status={t.status} /></td>
                    <td style={{ display: 'flex', gap: 8 }}>
                      {t.status === 'Pending' && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => updateTransfer(t.id, 'Approved')}>Approve</button>
                          <button className="btn btn-danger btn-sm" onClick={() => updateTransfer(t.id, 'Rejected')}>Reject</button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
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
                {availableAssets.map((a) => <option key={a.id} value={a.tag}>{a.tag} — {a.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Assign to</label>
              <select required value={aForm.assignedTo} onChange={(e) => setAForm({ ...aForm, assignedTo: e.target.value })}>
                <option value="">Select employee…</option>
                {employees.filter(e => e.status === 'Active').map((e) => <option key={e.id}>{e.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>From date</label>
              <input type="date" required value={aForm.from} onChange={(e) => setAForm({ ...aForm, from: e.target.value })} />
            </div>
            <div className="field">
              <label>To date</label>
              <input type="date" required value={aForm.to} onChange={(e) => setAForm({ ...aForm, to: e.target.value })} />
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
              <label>Asset tag</label>
              <input required value={tForm.asset} onChange={(e) => setTForm({ ...tForm, asset: e.target.value })} placeholder="e.g. AF-0231" />
            </div>
            <div className="field">
              <label>From department</label>
              <input required value={tForm.from} onChange={(e) => setTForm({ ...tForm, from: e.target.value })} />
            </div>
            <div className="field">
              <label>To department</label>
              <input required value={tForm.to} onChange={(e) => setTForm({ ...tForm, to: e.target.value })} />
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
