import { useState } from 'react';
import { useApp } from '../../context/AppContext';
import Modal from '../../components/Modal';
import StatusBadge from '../../components/StatusBadge';

const emptyForm = { name: '', head: '', parent: '', status: 'Active' };

export default function DepartmentTab() {
  const { departments, addDepartment, updateDepartment, toggleDepartmentStatus, employees } = useApp();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const eligibleHeads = employees.filter(
    (e) => e.status === 'Active' && (e.role === 'Department Head' || e.role === 'Employee')
  );

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (dept) => {
    setEditingId(dept.id);
    setForm({ name: dept.name, head: dept.head, parent: dept.parent || '', status: dept.status });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    const payload = { ...form, parent: form.parent || null };
    try {
      if (editingId) {
        await updateDepartment(editingId, payload);
      } else {
        await addDepartment(payload);
      }
      setModalOpen(false);
    } catch (err) {
      console.error(err);
    }
  };

  const parentName = (parentId) => departments.find((d) => d.id === parentId)?.name || '—';

  return (
    <div>
      <div className="panel-toolbar">
        <span className="panel-toolbar-title">
          <strong>{departments.length}</strong> departments
        </span>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          + Add department
        </button>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Department</th>
              <th>Department head</th>
              <th>Parent department</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {departments.length === 0 && (
              <tr className="empty-row">
                <td colSpan={5}>No departments yet. Add your first one.</td>
              </tr>
            )}
            {departments.map((d) => (
              <tr key={d.id}>
                <td style={{ fontWeight: 600 }}>{d.name}</td>
                <td>{d.head || '—'}</td>
                <td>{d.parent ? parentName(d.parent) : '—'}</td>
                <td>
                  <StatusBadge status={d.status} />
                </td>
                <td>
                  <div className="table-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => openEdit(d)}>
                      Edit
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => toggleDepartmentStatus(d.id)}
                    >
                      {d.status === 'Active' ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <Modal title={editingId ? 'Edit department' : 'Add department'} onClose={() => setModalOpen(false)}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="field">
              <label htmlFor="dept-name">Department name</label>
              <input
                id="dept-name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Engineering"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="dept-head">Department head</label>
              <select
                id="dept-head"
                value={form.head}
                onChange={(e) => setForm({ ...form, head: e.target.value })}
              >
                <option value="">Unassigned</option>
                {eligibleHeads.map((e) => (
                  <option key={e.id} value={e.name}>
                    {e.name}
                  </option>
                ))}
              </select>
              <span className="hint">Promote employees to Department Head from the Employee Directory tab.</span>
            </div>
            <div className="field">
              <label htmlFor="dept-parent">Parent department (optional)</label>
              <select
                id="dept-parent"
                value={form.parent}
                onChange={(e) => setForm({ ...form, parent: e.target.value })}
              >
                <option value="">None — top level</option>
                {departments
                  .filter((d) => d.id !== editingId)
                  .map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="dept-status">Status</label>
              <select
                id="dept-status"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setModalOpen(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                {editingId ? 'Save changes' : 'Add department'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
