import { useEffect, useState } from "react";
import { CategoriesAPI } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { Modal, ConfirmDialog, LoadingRow, EmptyState, Banner, BoolStamp, Pagination } from "../components/Kit";
import { IconPlus, IconEdit, IconTrash, IconTag, IconSearch } from "../components/Icons";

const emptyForm = { name: "", description: "", is_active: true };

export default function Categories() {
  const toast = useToast();
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [modal, setModal] = useState(null); // 'create' | 'edit'
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  function load() {
    setLoading(true);
    setError("");
    CategoriesAPI.list({ page, search: search || undefined })
      .then((res) => {
        const d = res.data;
        setItems(d.results ?? d);
        setCount(d.count ?? (d.results ?? d).length);
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load categories.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, [page]);

  function openCreate() {
    setForm(emptyForm);
    setFormError("");
    setModal("create");
  }
  function openEdit(item) {
    setForm({ name: item.name, description: item.description || "", is_active: item.is_active });
    setFormError("");
    setModal({ mode: "edit", id: item.id });
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setFormError("");
    try {
      if (modal === "create") {
        await CategoriesAPI.create(form);
        toast.success("Category added.");
      } else {
        await CategoriesAPI.update(modal.id, form);
        toast.success("Category updated.");
      }
      setModal(null);
      load();
    } catch (err) {
      setFormError(apiErrorMessage(err, "Couldn't save this category."));
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    setDeleting(true);
    try {
      await CategoriesAPI.remove(deleteTarget.id);
      toast.success("Category deleted.");
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't delete this category."));
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Inventory</div>
          <h1 className="page-title">Categories</h1>
          <p className="page-desc">Group products so stock and sales reports can roll up cleanly.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-primary" onClick={openCreate}>
            <IconPlus /> Add category
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrap">
          <IconSearch />
          <input
            placeholder="Search categories…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (setPage(1), load())}
          />
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => (setPage(1), load())}>Search</button>
      </div>

      {error && <Banner type="error">{error}</Banner>}

      <div className="panel">
        <div className="table-wrap">
          {loading ? (
            <LoadingRow />
          ) : items.length === 0 ? (
            <EmptyState icon={IconTag} title="No categories yet" body="Add your first category to start grouping products." />
          ) : (
            <table className="manifest">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr key={c.id}>
                    <td className="cell-strong">{c.name}</td>
                    <td className="cell-muted">{c.description || "—"}</td>
                    <td><BoolStamp value={c.is_active} trueLabel="Active" falseLabel="Inactive" /></td>
                    <td>
                      <div className="row-actions">
                        <button className="btn btn-secondary btn-sm btn-icon" onClick={() => openEdit(c)} aria-label="Edit"><IconEdit width={14} height={14} /></button>
                        <button className="btn btn-danger btn-sm btn-icon" onClick={() => setDeleteTarget(c)} aria-label="Delete"><IconTrash width={14} height={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <Pagination count={count} page={page} onPage={setPage} />
      </div>

      {modal && (
        <Modal
          title={modal === "create" ? "Add category" : "Edit category"}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" form="category-form" type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save category"}
              </button>
            </>
          }
        >
          {formError && <Banner type="error">{formError}</Banner>}
          <form id="category-form" onSubmit={submit}>
            <div className="field">
              <label>Name</label>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="field">
              <label>Description</label>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="checkbox-row">
              <input type="checkbox" id="cat-active" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
              <label htmlFor="cat-active" style={{ margin: 0 }}>Active</label>
            </div>
          </form>
        </Modal>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete category"
          body={`Delete "${deleteTarget.name}"? Products already assigned to it will keep their reference until reassigned.`}
          onConfirm={confirmDelete}
          onClose={() => setDeleteTarget(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}
