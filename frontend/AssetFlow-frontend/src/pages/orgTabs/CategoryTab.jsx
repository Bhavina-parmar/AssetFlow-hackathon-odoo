import { useState } from 'react';
import { useApp } from '../../context/AppContext';
import Modal from '../../components/Modal';

const emptyForm = { name: '', fields: [] };

export default function CategoryTab() {
  const { categories, addCategory, updateCategory, deleteCategory } = useApp();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [fieldDraft, setFieldDraft] = useState('');

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setFieldDraft('');
    setModalOpen(true);
  };

  const openEdit = (cat) => {
    setEditingId(cat.id);
    setForm({ name: cat.name, fields: cat.fields });
    setFieldDraft('');
    setModalOpen(true);
  };

  const addFieldDraft = () => {
    if (!fieldDraft.trim()) return;
    setForm((f) => ({
      ...f,
      fields: [...f.fields, { key: `f${Date.now()}`, label: fieldDraft.trim() }],
    }));
    setFieldDraft('');
  };

  const removeField = (key) => {
    setForm((f) => ({ ...f, fields: f.fields.filter((field) => field.key !== key) }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    if (editingId) {
      updateCategory(editingId, form);
    } else {
      addCategory(form);
    }
    setModalOpen(false);
  };

  return (
    <div>
      <div className="panel-toolbar">
        <span className="panel-toolbar-title">
          <strong>{categories.length}</strong> categories
        </span>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          + Add category
        </button>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Category-specific fields</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {categories.length === 0 && (
              <tr className="empty-row">
                <td colSpan={3}>No categories yet. Add your first one.</td>
              </tr>
            )}
            {categories.map((c) => (
              <tr key={c.id}>
                <td style={{ fontWeight: 600 }}>{c.name}</td>
                <td>
                  {c.fields.length === 0 ? (
                    <span style={{ color: 'var(--muted)' }}>None</span>
                  ) : (
                    <div className="chip-list">
                      {c.fields.map((f) => (
                        <span className="chip" key={f.key}>
                          {f.label}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td>
                  <div className="table-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => openEdit(c)}>
                      Edit
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ color: 'var(--danger)' }}
                      onClick={() => deleteCategory(c.id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <Modal title={editingId ? 'Edit category' : 'Add category'} onClose={() => setModalOpen(false)}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="field">
              <label htmlFor="cat-name">Category name</label>
              <input
                id="cat-name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Electronics"
                required
              />
            </div>

            <div className="field">
              <label>Category-specific fields (optional)</label>
              <span className="hint">e.g. "Warranty period" for Electronics, "Plate number" for Vehicles.</span>
              <div className="category-fields-list">
                {form.fields.map((f) => (
                  <div className="category-field-row" key={f.key}>
                    <input value={f.label} readOnly />
                    <button type="button" onClick={() => removeField(f.key)} aria-label={`Remove ${f.label}`}>
                      ✕
                    </button>
                  </div>
                ))}
                <div className="category-field-row">
                  <input
                    value={fieldDraft}
                    onChange={(e) => setFieldDraft(e.target.value)}
                    placeholder="Field name"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addFieldDraft();
                      }
                    }}
                  />
                  <button type="button" onClick={addFieldDraft} aria-label="Add field" style={{ color: 'var(--accent)' }}>
                    +
                  </button>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setModalOpen(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                {editingId ? 'Save changes' : 'Add category'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
