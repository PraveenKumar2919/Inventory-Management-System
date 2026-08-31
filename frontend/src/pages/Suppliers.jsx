import { useEffect, useState } from "react";
import { SuppliersAPI } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { Modal, ConfirmDialog, LoadingRow, EmptyState, Banner, BoolStamp, Pagination } from "../components/Kit";
import { IconPlus, IconEdit, IconTrash, IconTruck, IconSearch } from "../components/Icons";

const emptyForm = { name: "", company_name: "", email: "", phone: "", address: "", is_active: true };

export default function Suppliers() {
  const toast = useToast();
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [modal, setModal] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  function load() {
    setLoading(true);
    setError("");
    SuppliersAPI.list({ page, search: search || undefined })
      .then((res) => {
        const d = res.data;
        setItems(d.results ?? d);
        setCount(d.count ?? (d.results ?? d).length);
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load suppliers.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, [page]);

  function openCreate() {
    setForm(emptyForm);
    setFormError("");
    setModal("create");
  }
  function openEdit(item) {
    setForm({
      name: item.name || "",
      company_name: item.company_name || "",
      email: item.email || "",
      phone: item.phone || "",
      address: item.address || "",
      is_active: item.is_active,
    });
    setFormError("");
    setModal({ mode: "edit", id: item.id });
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setFormError("");
    try {
      if (modal === "create") {
        await SuppliersAPI.create(form);
        toast.success("Supplier added.");
      } else {
        await SuppliersAPI.update(modal.id, form);
        toast.success("Supplier updated.");
      }
      setModal(null);
      load();
    } catch (err) {
      setFormError(apiErrorMessage(err, "Couldn't save this supplier."));
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    setDeleting(true);
    try {
      await SuppliersAPI.remove(deleteTarget.id);
      toast.success("Supplier deleted.");
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't delete this supplier."));
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Inventory</div>
          <h1 className="page-title">Suppliers</h1>
          <p className="page-desc">Vendors that stock your products, with contact details for reorders.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-primary" onClick={openCreate}>
            <IconPlus /> Add supplier
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrap">
          <IconSearch />
          <input
            placeholder="Search suppliers…"
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
            <EmptyState icon={IconTruck} title="No suppliers yet" body="Add a supplier to start tracking where stock comes from." />
          ) : (
            <table className="manifest">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Company</th>
                  <th>Contact</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => (
                  <tr key={s.id}>
                    <td className="cell-strong">{s.name}</td>
                    <td className="cell-muted">{s.company_name || "—"}</td>
                    <td className="cell-muted">
                      {s.email || "—"}
                      {s.phone ? <div className="mono" style={{ fontSize: 11.5 }}>{s.phone}</div> : null}
                    </td>
                    <td><BoolStamp value={s.is_active} trueLabel="Active" falseLabel="Inactive" /></td>
                    <td>
                      <div className="row-actions">
                        <button className="btn btn-secondary btn-sm btn-icon" onClick={() => openEdit(s)} aria-label="Edit"><IconEdit width={14} height={14} /></button>
                        <button className="btn btn-danger btn-sm btn-icon" onClick={() => setDeleteTarget(s)} aria-label="Delete"><IconTrash width={14} height={14} /></button>
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
          title={modal === "create" ? "Add supplier" : "Edit supplier"}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" form="supplier-form" type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save supplier"}
              </button>
            </>
          }
        >
          {formError && <Banner type="error">{formError}</Banner>}
          <form id="supplier-form" onSubmit={submit}>
            <div className="field-row">
              <div className="field">
                <label>Contact name</label>
                <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="field">
                <label>Company name</label>
                <input value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
              </div>
            </div>
            <div className="field-row">
              <div className="field">
                <label>Email</label>
                <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div className="field">
                <label>Phone</label>
                <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              </div>
            </div>
            <div className="field">
              <label>Address</label>
              <textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            </div>
            <div className="checkbox-row">
              <input type="checkbox" id="sup-active" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
              <label htmlFor="sup-active" style={{ margin: 0 }}>Active</label>
            </div>
          </form>
        </Modal>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete supplier"
          body={`Delete "${deleteTarget.name}"? This can't be undone.`}
          onConfirm={confirmDelete}
          onClose={() => setDeleteTarget(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}
