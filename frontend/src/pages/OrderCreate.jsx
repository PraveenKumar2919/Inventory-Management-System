import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { OrdersAPI, CustomersAPI, ProductsAPI, fetchAllPages } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { Banner } from "../components/Kit";
import { IconPlus, IconTrash } from "../components/Icons";

const money = (v) => `₹${Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;

export default function OrderCreate() {
  const navigate = useNavigate();
  const toast = useToast();

  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loadingRefs, setLoadingRefs] = useState(true);

  const [customer, setCustomer] = useState("");
  const [shippingAddress, setShippingAddress] = useState("");
  const [notes, setNotes] = useState("");
  const [taxAmount, setTaxAmount] = useState("0.00");
  const [discountAmount, setDiscountAmount] = useState("0.00");
  const [lines, setLines] = useState([{ product: "", quantity: 1 }]);

  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchAllPages((p) => CustomersAPI.list({ ...p, is_active: true })),
      fetchAllPages((p) => ProductsAPI.list(p)),
    ])
      .then(([c, p]) => {
        setCustomers(c);
        setProducts(p.filter((x) => x.is_active));
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load customers/products.")))
      .finally(() => setLoadingRefs(false));
  }, []);

  function productById(id) {
    return products.find((p) => String(p.id) === String(id));
  }

  function updateLine(idx, patch) {
    setLines((ls) => ls.map((l, i) => (i === idx ? { ...l, ...patch } : l)));
  }
  function addLine() {
    setLines((ls) => [...ls, { product: "", quantity: 1 }]);
  }
  function removeLine(idx) {
    setLines((ls) => ls.filter((_, i) => i !== idx));
  }

  const subtotal = useMemo(() => {
    return lines.reduce((sum, l) => {
      const p = productById(l.product);
      if (!p || !l.quantity) return sum;
      return sum + Number(p.selling_price) * Number(l.quantity);
    }, 0);
  }, [lines, products]);

  const total = Math.max(0, subtotal + Number(taxAmount || 0) - Number(discountAmount || 0));

  async function submit(e) {
    e.preventDefault();
    setError("");

    const validLines = lines.filter((l) => l.product && Number(l.quantity) > 0);
    if (!customer) return setError("Choose a customer for this order.");
    if (validLines.length === 0) return setError("Add at least one product line.");

    setSaving(true);
    try {
      const res = await OrdersAPI.create({
        customer: Number(customer),
        shipping_address: shippingAddress || "",
        notes: notes || "",
        tax_amount: taxAmount || "0.00",
        discount_amount: discountAmount || "0.00",
        items: validLines.map((l) => ({ product: Number(l.product), quantity: Number(l.quantity) })),
      });
      toast.success(`Order ${res.data.order_number} created.`);
      navigate(`/orders/${res.data.id}`);
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this order."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Order Desk</div>
          <h1 className="page-title">New order</h1>
          <p className="page-desc">Pick a customer, add line items — stock is checked and reserved automatically.</p>
        </div>
      </div>

      {error && <Banner type="error">{error}</Banner>}

      <form onSubmit={submit} style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 16 }} className="dash-grid">
        <div className="panel">
          <div className="panel-head"><h3>Line items</h3></div>
          <div className="panel-body">
            {loadingRefs ? (
              <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Loading products…</p>
            ) : (
              <>
                {lines.map((l, idx) => {
                  const p = productById(l.product);
                  return (
                    <div key={idx} style={{ display: "grid", gridTemplateColumns: "1fr 90px 100px 34px", gap: 8, marginBottom: 10, alignItems: "center" }}>
                      <select value={l.product} onChange={(e) => updateLine(idx, { product: e.target.value })} required>
                        <option value="">Select product…</option>
                        {products.map((pr) => (
                          <option key={pr.id} value={pr.id} disabled={pr.quantity === 0}>
                            {pr.product_name} ({pr.product_code}) — {money(pr.selling_price)} · {pr.quantity} left
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        min="1"
                        max={p?.quantity || undefined}
                        value={l.quantity}
                        onChange={(e) => updateLine(idx, { quantity: e.target.value })}
                      />
                      <div className="mono cell-muted" style={{ fontSize: 12.5, textAlign: "right" }}>
                        {p ? money(Number(p.selling_price) * Number(l.quantity || 0)) : "—"}
                      </div>
                      <button type="button" className="btn btn-danger btn-icon" onClick={() => removeLine(idx)} disabled={lines.length === 1} aria-label="Remove line">
                        <IconTrash width={14} height={14} />
                      </button>
                    </div>
                  );
                })}
                <button type="button" className="btn btn-secondary btn-sm" onClick={addLine}>
                  <IconPlus width={13} height={13} /> Add line
                </button>
              </>
            )}

            <hr className="divider" />

            <div className="field">
              <label>Shipping address</label>
              <textarea value={shippingAddress} onChange={(e) => setShippingAddress(e.target.value)} />
            </div>
            <div className="field">
              <label>Notes</label>
              <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>
          </div>
        </div>

        <div>
          <div className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-head"><h3>Customer</h3></div>
            <div className="panel-body">
              <div className="field" style={{ marginBottom: 0 }}>
                <label>Order for</label>
                <select required value={customer} onChange={(e) => setCustomer(e.target.value)}>
                  <option value="">Select customer…</option>
                  {customers.map((c) => <option key={c.id} value={c.id}>{c.customer_name}</option>)}
                </select>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-head"><h3>Totals</h3></div>
            <div className="panel-body">
              <div className="field-row">
                <div className="field">
                  <label>Tax amount</label>
                  <input type="number" step="0.01" min="0" value={taxAmount} onChange={(e) => setTaxAmount(e.target.value)} />
                </div>
                <div className="field">
                  <label>Discount</label>
                  <input type="number" step="0.01" min="0" value={discountAmount} onChange={(e) => setDiscountAmount(e.target.value)} />
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 6 }}>
                <span className="cell-muted">Subtotal</span><span className="mono">{money(subtotal)}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 15, fontWeight: 700, marginBottom: 16 }}>
                <span>Total</span><span className="mono">{money(total)}</span>
              </div>
              <button className="btn btn-primary btn-block" type="submit" disabled={saving}>
                {saving ? "Placing order…" : "Place order"}
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
