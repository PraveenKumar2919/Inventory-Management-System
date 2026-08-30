import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { OrdersAPI } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { LoadingRow, Banner, Stamp, ConfirmDialog } from "../components/Kit";

const money = (v) => `₹${Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;

const STATUS_TRANSITIONS = {
  PENDING: ["CONFIRMED", "CANCELLED"],
  CONFIRMED: ["PROCESSING", "CANCELLED"],
  PROCESSING: ["SHIPPED", "CANCELLED"],
  SHIPPED: ["DELIVERED"],
  DELIVERED: [],
  CANCELLED: [],
};

const PAYMENT_TRANSITIONS = {
  PENDING: ["PAID", "FAILED"],
  FAILED: ["PENDING", "PAID"],
  PAID: ["REFUNDED"],
  REFUNDED: [],
};

export default function OrderDetail() {
  const { id } = useParams();
  const toast = useToast();

  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);

  function load() {
    setLoading(true);
    setError("");
    OrdersAPI.detail(id)
      .then((res) => setOrder(res.data))
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load this order.")))
      .finally(() => setLoading(false));
  }
  useEffect(load, [id]);

  async function changeStatus(newStatus) {
    setBusy(true);
    try {
      await OrdersAPI.updateStatus(id, newStatus);
      toast.success(`Order marked ${newStatus.toLowerCase()}.`);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't update the status."));
    } finally {
      setBusy(false);
    }
  }

  async function changePayment(newPayment) {
    setBusy(true);
    try {
      await OrdersAPI.updatePayment(id, newPayment);
      toast.success(`Payment marked ${newPayment.toLowerCase()}.`);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't update payment status."));
    } finally {
      setBusy(false);
    }
  }

  async function cancelOrder() {
    setBusy(true);
    try {
      await OrdersAPI.cancel(id);
      toast.success("Order cancelled and stock restored.");
      setConfirmCancel(false);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't cancel this order."));
      setConfirmCancel(false);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <LoadingRow label="Loading order…" />;
  if (error) return <Banner type="error">{error}</Banner>;
  if (!order) return null;

  const statusOptions = STATUS_TRANSITIONS[order.status] || [];
  const paymentOptions = PAYMENT_TRANSITIONS[order.payment_status] || [];
  const canCancel = order.status !== "CANCELLED" && order.status !== "DELIVERED" && order.payment_status !== "PAID";

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">
            <Link to="/orders" style={{ textDecoration: "underline" }}>Orders</Link> / {order.order_number}
          </div>
          <h1 className="page-title mono">{order.order_number}</h1>
          <p className="page-desc">
            Placed {new Date(order.order_date).toLocaleString("en-IN")} for <strong>{order.customer_name}</strong>
          </p>
        </div>
        <div className="page-actions" style={{ gap: 8 }}>
          <Stamp value={order.status} />
          <Stamp value={order.payment_status} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 16 }} className="dash-grid">
        <div className="panel">
          <div className="panel-head"><h3>Items</h3><span className="pill-count">{order.item_count} lines</span></div>
          <div className="table-wrap">
            <table className="manifest">
              <thead>
                <tr>
                  <th>Product</th>
                  <th className="cell-num">Qty</th>
                  <th className="cell-num">Unit price</th>
                  <th className="cell-num">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {order.items.map((it) => (
                  <tr key={it.id}>
                    <td>
                      <div className="cell-strong">{it.product_name}</div>
                      <div className="cell-code">{it.product_code}</div>
                    </td>
                    <td className="cell-num">{it.quantity}</td>
                    <td className="cell-num">{money(it.unit_price)}</td>
                    <td className="cell-num">{money(it.subtotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="panel-body" style={{ borderTop: "1px solid var(--line)" }}>
            <div style={{ maxWidth: 280, marginLeft: "auto", display: "grid", gap: 6, fontSize: 13 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}><span className="cell-muted">Subtotal</span><span className="mono">{money(order.subtotal)}</span></div>
              <div style={{ display: "flex", justifyContent: "space-between" }}><span className="cell-muted">Tax</span><span className="mono">{money(order.tax_amount)}</span></div>
              <div style={{ display: "flex", justifyContent: "space-between" }}><span className="cell-muted">Discount</span><span className="mono">-{money(order.discount_amount)}</span></div>
              <hr className="divider" style={{ margin: "4px 0" }} />
              <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: 15 }}><span>Total</span><span className="mono">{money(order.total_amount)}</span></div>
            </div>
          </div>
          {(order.shipping_address || order.notes) && (
            <div className="panel-body" style={{ borderTop: "1px solid var(--line)" }}>
              <div className="kv-grid">
                {order.shipping_address && (
                  <div className="kv-item">
                    <div className="kv-label">Shipping address</div>
                    <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>{order.shipping_address}</div>
                  </div>
                )}
                {order.notes && (
                  <div className="kv-item">
                    <div className="kv-label">Notes</div>
                    <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>{order.notes}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="panel">
            <div className="panel-head"><h3>Order status</h3></div>
            <div className="panel-body">
              <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 10 }}>Current: <Stamp value={order.status} /></p>
              {statusOptions.length === 0 ? (
                <p style={{ fontSize: 12.5, color: "var(--text-muted)" }}>No further transitions available.</p>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {statusOptions.map((s) => (
                    <button key={s} className="btn btn-secondary btn-sm" disabled={busy} onClick={() => changeStatus(s)}>
                      Mark {s.toLowerCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-head"><h3>Payment status</h3></div>
            <div className="panel-body">
              <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 10 }}>Current: <Stamp value={order.payment_status} /></p>
              {paymentOptions.length === 0 ? (
                <p style={{ fontSize: 12.5, color: "var(--text-muted)" }}>No further transitions available.</p>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {paymentOptions.map((s) => (
                    <button key={s} className="btn btn-secondary btn-sm" disabled={busy} onClick={() => changePayment(s)}>
                      Mark {s.toLowerCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {canCancel && (
            <div className="panel">
              <div className="panel-head"><h3>Cancel order</h3></div>
              <div className="panel-body">
                <p style={{ fontSize: 12.5, color: "var(--text-secondary)", marginBottom: 12 }}>
                  Restores reserved stock and marks the order cancelled. This can't be undone.
                </p>
                <button className="btn btn-danger btn-block" disabled={busy} onClick={() => setConfirmCancel(true)}>
                  Cancel this order
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {confirmCancel && (
        <ConfirmDialog
          title="Cancel order"
          body={`Cancel ${order.order_number}? Reserved stock will be returned to inventory.`}
          confirmLabel="Cancel order"
          onConfirm={cancelOrder}
          onClose={() => setConfirmCancel(false)}
          loading={busy}
        />
      )}
    </div>
  );
}
