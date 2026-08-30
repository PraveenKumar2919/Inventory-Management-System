import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { OrdersAPI } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { LoadingRow, EmptyState, Banner, Stamp, Pagination } from "../components/Kit";
import { IconPlus, IconClipboard, IconSearch } from "../components/Icons";

const money = (v) => `₹${Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;

const STATUS_OPTIONS = ["", "PENDING", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"];
const PAYMENT_OPTIONS = ["", "PENDING", "PAID", "FAILED", "REFUNDED"];

export default function OrdersList() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [payment, setPayment] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function load() {
    setLoading(true);
    setError("");
    OrdersAPI.list({ page, search: search || undefined, status: status || undefined, payment_status: payment || undefined, ordering: "-created_at" })
      .then((res) => {
        const d = res.data;
        setItems(d.results ?? d);
        setCount(d.count ?? (d.results ?? d).length);
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load orders.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, [page, status, payment]);

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Order Desk</div>
          <h1 className="page-title">Orders</h1>
          <p className="page-desc">Every order from cart to delivery, with status and payment tracked side by side.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-primary" onClick={() => navigate("/orders/new")}>
            <IconPlus /> New order
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrap">
          <IconSearch />
          <input
            placeholder="Search order #, customer…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (setPage(1), load())}
          />
        </div>
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
          {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s || "All statuses"}</option>)}
        </select>
        <select value={payment} onChange={(e) => { setPayment(e.target.value); setPage(1); }}>
          {PAYMENT_OPTIONS.map((s) => <option key={s} value={s}>{s || "All payments"}</option>)}
        </select>
        <button className="btn btn-secondary btn-sm" onClick={() => (setPage(1), load())}>Search</button>
      </div>

      {error && <Banner type="error">{error}</Banner>}

      <div className="panel">
        <div className="table-wrap">
          {loading ? (
            <LoadingRow />
          ) : items.length === 0 ? (
            <EmptyState icon={IconClipboard} title="No orders found" body="Try clearing filters, or create a new order." />
          ) : (
            <table className="manifest">
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Items</th>
                  <th>Status</th>
                  <th>Payment</th>
                  <th style={{ textAlign: "right" }}>Total</th>
                </tr>
              </thead>
              <tbody>
                {items.map((o) => (
                  <tr key={o.id} onClick={() => navigate(`/orders/${o.id}`)} style={{ cursor: "pointer" }}>
                    <td className="cell-code cell-strong">{o.order_number}</td>
                    <td>{o.customer_name}</td>
                    <td className="cell-muted">{new Date(o.order_date).toLocaleDateString("en-IN")}</td>
                    <td className="cell-muted">{o.item_count}</td>
                    <td><Stamp value={o.status} /></td>
                    <td><Stamp value={o.payment_status} /></td>
                    <td className="cell-num">{money(o.total_amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <Pagination count={count} page={page} onPage={setPage} />
      </div>
    </div>
  );
}
