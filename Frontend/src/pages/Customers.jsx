import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CustomersAPI } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { Modal, ConfirmDialog, LoadingRow, EmptyState, Banner, BoolStamp, Pagination } from "../components/Kit";
import { IconPlus, IconEdit, IconTrash, IconUsers, IconSearch, IconArrowUpRight } from "../components/Icons";

const emptyForm = { customer_name: "", customer_since: "", email: "", phone: "", address: "", is_active: true };

export default function Customers() {
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
    CustomersAPI.list({ page, search: search || undefined })
      .then((res) => {
        const d = res.data;
        setItems(d.results ?? d);
        setCount(d.count ?? (d.results ?? d).length);
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load customers.")))
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
      customer_name: item.customer_name || "",
      customer_since: item.customer_since || "",
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
    const payload = { ...form, customer_since: form.customer_since || null };
    try {
      if (modal === "create") {
        await CustomersAPI.create(payload);
        toast.success("Customer added.");
      } else {
        await CustomersAPI.update(modal.id, payload);
        toast.success("Customer updated.");
      }
      setModal(null);
      load();
    } catch (err) {
      setFormError(apiErrorMessage(err, "Couldn't save this customer."));
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    setDeleting(true);
    try {
      await CustomersAPI.remove(deleteTarget.id);
      toast.success("Customer deleted.");
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't delete this customer."));
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Order Desk</div>
          <h1 className="page-title">Customers</h1>
          <p className="page-desc">Everyone who has an account to place orders against.</p>
        </div>
        <div className="page-actions">
          <Link to="/orders" className="btn btn-secondary">
            View orders <IconArrowUpRight width={13} height={13} />
          </Link>
          <button className="btn btn-primary" onClick={openCreate}>
            <IconPlus /> Add customer
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrap">
          <IconSearch />
          <input
            placeholder="Search name, email, phone…"
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
            <EmptyState icon={IconUsers} title="No customers yet" body="Add your first customer to start creating orders." />
          ) : (
            <table className="manifest">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Contact</th>
                  <th>Customer since</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr key={c.id}>
                    <td className="cell-strong">{c.customer_name}</td>
                    <td className="cell-muted">
                      {c.email || "—"}
                      {c.phone ? <div className="mono" style={{ fontSize: 11.5 }}>{c.phone}</div> : null}
                    </td>
                    <td className="cell-muted">{c.customer_since || "—"}</td>
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
          title={modal === "create" ? "Add customer" : "Edit customer"}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" form="customer-form" type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save customer"}
              </button>
            </>
          }
        >
          {formError && <Banner type="error">{formError}</Banner>}
          <form id="customer-form" onSubmit={submit}>
            <div className="field">
              <label>Full name</label>
              <input required value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} />
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
            <div className="field-row">
              <div className="field">
                <label>Customer since</label>
                <input type="date" value={form.customer_since} onChange={(e) => setForm({ ...form, customer_since: e.target.value })} />
              </div>
              <div className="field" style={{ display: "flex", alignItems: "flex-end" }}>
                <div className="checkbox-row">
                  <input type="checkbox" id="cu-active" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
                  <label htmlFor="cu-active" style={{ margin: 0 }}>Active</label>
                </div>
              </div>
            </div>
            <div className="field">
              <label>Address</label>
              <textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            </div>
          </form>
        </Modal>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete customer"
          body={`Delete "${deleteTarget.customer_name}"? This can't be undone.`}
          onConfirm={confirmDelete}
          onClose={() => setDeleteTarget(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}
