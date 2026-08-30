import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { InventoryDashboardAPI, OrdersAPI } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { LoadingRow, Banner, Stamp, EmptyState } from "../components/Kit";
import { IconArrowUpRight, IconClipboard } from "../components/Icons";

const money = (v) =>
  `₹${Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    Promise.all([
      InventoryDashboardAPI.summary(),
      OrdersAPI.list({ page_size: 6, ordering: "-created_at" }),
    ])
      .then(([dash, ord]) => {
        if (!alive) return;
        setData(dash.data);
        setOrders(ord.data.results || ord.data || []);
      })
      .catch((err) => alive && setError(apiErrorMessage(err, "Couldn't load the dashboard.")))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, []);

  if (loading) return <LoadingRow label="Loading manifest…" />;
  if (error) return <Banner type="error">{error}</Banner>;
  if (!data) return null;

  const cards = [
    { label: "Stock Value", value: money(data.inventory.total_stock_value), sub: `${data.inventory.total_stock} units on hand`, accent: "var(--freight-blue)" },
    { label: "Sales — This Month", value: money(data.sales.this_month), sub: `Today: ${money(data.sales.today)}`, accent: "var(--dock-green)" },
    { label: "Low Stock", value: data.products.low_stock, sub: "Products at or below minimum", accent: "var(--signal-amber)", link: "/products?stock=low" },
    { label: "Out of Stock", value: data.products.out_of_stock, sub: "Active products with zero units", accent: "var(--alert-red)", link: "/products?stock=out" },
  ];

  const orderCards = [
    { label: "Total Orders", value: data.orders.total },
    { label: "Pending", value: data.orders.pending },
    { label: "Processing", value: data.orders.processing },
    { label: "Delivered", value: data.orders.delivered },
  ];

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Manifest — {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}</div>
          <h1 className="page-title">Operations overview</h1>
          <p className="page-desc">
            {data.products.total} products across {data.categories.total} categories, {data.suppliers.total} suppliers on file.
          </p>
        </div>
      </div>

      <div className="stat-grid">
        {cards.map((c) => (
          <Link to={c.link || "#"} key={c.label} className="stat-card" style={{ "--accent": c.accent, cursor: c.link ? "pointer" : "default" }}>
            <div className="stat-label">{c.label}</div>
            <div className="stat-value">{c.value}</div>
            <div className="stat-sub">{c.sub}</div>
          </Link>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 16 }} className="dash-grid">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h3>Recent orders</h3>
              <div className="panel-head-sub">Latest activity across the order desk</div>
            </div>
            <Link to="/orders" className="btn btn-secondary btn-sm">
              View all <IconArrowUpRight width={13} height={13} />
            </Link>
          </div>
          <div className="table-wrap">
            {orders.length === 0 ? (
              <EmptyState icon={IconClipboard} title="No orders yet" body="Orders will show up here once created." />
            ) : (
              <table className="manifest">
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>Customer</th>
                    <th>Status</th>
                    <th>Payment</th>
                    <th style={{ textAlign: "right" }}>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.id} onClick={() => (window.location.href = `/orders/${o.id}`)} style={{ cursor: "pointer" }}>
                      <td className="cell-code cell-strong">{o.order_number}</td>
                      <td>{o.customer_name}</td>
                      <td><Stamp value={o.status} /></td>
                      <td><Stamp value={o.payment_status} /></td>
                      <td className="cell-num">{money(o.total_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-head">
            <h3>Order pipeline</h3>
          </div>
          <div className="panel-body" style={{ display: "grid", gap: 12 }}>
            {orderCards.map((o) => (
              <div key={o.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{o.label}</span>
                <span className="mono" style={{ fontWeight: 600, fontSize: 15 }}>{o.value}</span>
              </div>
            ))}
            <hr className="divider" style={{ margin: "4px 0" }} />
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>Shipped</span>
              <span className="mono" style={{ fontWeight: 600 }}>{data.orders.shipped}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>Cancelled</span>
              <span className="mono" style={{ fontWeight: 600, color: "var(--alert-red)" }}>{data.orders.cancelled}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
