import { useEffect, useState } from "react";
import { TransactionsAPI, ProductsAPI, fetchAllPages } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { Modal, LoadingRow, EmptyState, Banner, Stamp, Pagination } from "../components/Kit";
import { IconSwap, IconPlus } from "../components/Icons";

const emptyStock = { product_id: "", quantity: 1, reference: "", notes: "" };

export default function Transactions() {
  const toast = useToast();
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [typeFilter, setTypeFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [products, setProducts] = useState([]);

  const [modal, setModal] = useState(null); // 'in' | 'out'
  const [form, setForm] = useState(emptyStock);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    fetchAllPages((p) => ProductsAPI.list(p)).then(setProducts).catch(() => {});
  }, []);

  function load() {
    setLoading(true);
    setError("");
    TransactionsAPI.list({ page, transaction_type: typeFilter || undefined })
      .then((res) => {
        const d = res.data;
        setItems(d.results ?? []);
        setCount(d.count ?? 0);
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load transactions.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, [page, typeFilter]);

  function openStock(kind) {
    setForm(emptyStock);
    setFormError("");
    setModal(kind);
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setFormError("");
    const payload = { ...form, product_id: Number(form.product_id), quantity: Number(form.quantity) };
    try {
      if (modal === "in") {
        await TransactionsAPI.stockIn(payload);
        toast.success("Stock added.");
      } else {
        await TransactionsAPI.stockOut(payload);
        toast.success("Stock removed.");
      }
      setModal(null);
      setPage(1);
      load();
    } catch (err) {
      setFormError(apiErrorMessage(err, "Couldn't record this transaction."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Inventory</div>
          <h1 className="page-title">Stock transactions</h1>
          <p className="page-desc">A running ledger of every stock movement — in, out, adjustment or return.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={() => openStock("out")}>
            <IconSwap /> Stock out
          </button>
          <button className="btn btn-primary" onClick={() => openStock("in")}>
            <IconPlus /> Stock in
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="seg">
          {["", "IN", "OUT"].map((t) => (
            <button key={t} className={typeFilter === t ? "active" : ""} onClick={() => { setTypeFilter(t); setPage(1); }}>
              {t === "" ? "All" : t === "IN" ? "Stock in" : "Stock out"}
            </button>
          ))}
        </div>
      </div>

      {error && <Banner type="error">{error}</Banner>}

      <div className="panel">
        <div className="table-wrap">
          {loading ? (
            <LoadingRow />
          ) : items.length === 0 ? (
            <EmptyState icon={IconSwap} title="No transactions yet" body="Stock movements will appear here as you add or remove inventory." />
          ) : (
            <table className="manifest">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Type</th>
                  <th>Qty</th>
                  <th>Before → After</th>
                  <th>Reference</th>
                  <th>When</th>
                </tr>
              </thead>
              <tbody>
                {items.map((t) => (
                  <tr key={t.id}>
                    <td>
                      <div className="cell-strong">{t.product_name}</div>
                      <div className="cell-code">{t.product_code}</div>
                    </td>
                    <td><Stamp value={t.transaction_type} /></td>
                    <td className="cell-num">{t.quantity}</td>
                    <td className="mono cell-muted">{t.previous_quantity} → {t.new_quantity}</td>
                    <td className="cell-muted">{t.reference || "—"}</td>
                    <td className="cell-muted">{new Date(t.created_at).toLocaleString("en-IN")}</td>
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
          title={modal === "in" ? "Stock in" : "Stock out"}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" form="stock-form" type="submit" disabled={saving}>
                {saving ? "Recording…" : modal === "in" ? "Add stock" : "Remove stock"}
              </button>
            </>
          }
        >
          {formError && <Banner type="error">{formError}</Banner>}
          <form id="stock-form" onSubmit={submit}>
            <div className="field">
              <label>Product</label>
              <select required value={form.product_id} onChange={(e) => setForm({ ...form, product_id: e.target.value })}>
                <option value="">Select a product…</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>{p.product_name} ({p.product_code}) — {p.quantity} {p.unit} on hand</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Quantity</label>
              <input type="number" min="1" required value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
            </div>
            <div className="field">
              <label>Reference</label>
              <input value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} placeholder="PO number, invoice…" />
            </div>
            <div className="field">
              <label>Notes</label>
              <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
