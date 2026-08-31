import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import reports, { REPORT_GROUPS } from "../reportsConfig";
import {
  IconDashboard,
  IconBox,
  IconTag,
  IconTruck,
  IconSwap,
  IconUsers,
  IconClipboard,
  IconChart,
  IconChevron,
  IconMenu,
  IconLogout,
} from "./Icons";

const NAV = [
  { to: "/", label: "Dashboard", icon: IconDashboard, end: true },
];

const INVENTORY_NAV = [
  { to: "/products", label: "Products", icon: IconBox },
  { to: "/categories", label: "Categories", icon: IconTag },
  { to: "/suppliers", label: "Suppliers", icon: IconTruck },
  { to: "/transactions", label: "Transactions", icon: IconSwap },
];

const SALES_NAV = [
  { to: "/customers", label: "Customers", icon: IconUsers },
  { to: "/orders", label: "Orders", icon: IconClipboard },
];

function pageTitleFor(pathname) {
  const map = {
    "/": ["Overview", "Dashboard"],
    "/products": ["Inventory", "Products"],
    "/categories": ["Inventory", "Categories"],
    "/suppliers": ["Inventory", "Suppliers"],
    "/transactions": ["Inventory", "Stock Transactions"],
    "/customers": ["Order Desk", "Customers"],
    "/orders": ["Order Desk", "Orders"],
  };
  if (map[pathname]) return map[pathname];
  if (pathname.startsWith("/orders/")) return ["Order Desk", "Order Detail"];
  if (pathname.startsWith("/reports/")) return ["Analytics", "Report"];
  return ["Consign", ""];
}

export default function Layout() {
  const [open, setOpen] = useState(false);
  const [reportsOpen, setReportsOpen] = useState(true);
  const { user, logout } = useAuth();
  const location = useLocation();
  const [eyebrow, title] = pageTitleFor(location.pathname);

  const grouped = REPORT_GROUPS.map((g) => ({
    group: g,
    items: reports.filter((r) => r.group === g),
  }));

  const initials = (user?.username || "OP").slice(0, 2).toUpperCase();

  return (
    <div className="app-shell">
      <div className={`scrim ${open ? "show" : ""}`} onClick={() => setOpen(false)} />
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="sidebar-brand">
          <div className="sidebar-brand-mark">C·</div>
          <div>
            <div className="sidebar-brand-text">Consign</div>
            <div className="sidebar-brand-sub">Ops Console</div>
          </div>
        </div>
        <nav className="sidebar-scroll">
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={({ isActive }) => `side-link ${isActive ? "active" : ""}`} onClick={() => setOpen(false)}>
              <item.icon />
              {item.label}
            </NavLink>
          ))}

          <div className="side-group-label">Inventory</div>
          {INVENTORY_NAV.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `side-link ${isActive ? "active" : ""}`} onClick={() => setOpen(false)}>
              <item.icon />
              {item.label}
            </NavLink>
          ))}

          <div className="side-group-label">Order Desk</div>
          {SALES_NAV.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `side-link ${isActive ? "active" : ""}`} onClick={() => setOpen(false)}>
              <item.icon />
              {item.label}
            </NavLink>
          ))}

          <div className="side-group-label">Analytics</div>
          <NavLink to="/reports" end className={({ isActive }) => `side-link ${isActive ? "active" : ""}`} onClick={() => setOpen(false)}>
            <IconChart /> Reports desk
          </NavLink>
          <div className={`side-link sidebar-toggle-reports ${reportsOpen ? "open" : ""}`} onClick={() => setReportsOpen((v) => !v)}>
            <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <IconChart /> All reports
            </span>
            <IconChevron className="chev" />
          </div>
          {reportsOpen && (
            <div className="side-sub">
              {grouped.map(({ group, items }) => (
                <div key={group}>
                  {items.map((r) => (
                    <NavLink key={r.slug} to={`/reports/${r.slug}`} className={({ isActive }) => `side-link ${isActive ? "active" : ""}`} onClick={() => setOpen(false)}>
                      {r.title}
                    </NavLink>
                  ))}
                </div>
              ))}
            </div>
          )}
        </nav>
      </aside>

      <div className="main-col">
        <header className="topbar">
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button className="menu-btn" onClick={() => setOpen(true)} aria-label="Open menu">
              <IconMenu width={20} height={20} />
            </button>
            <div>
              <div className="topbar-eyebrow">{eyebrow}</div>
              <div className="topbar-title">{title}</div>
            </div>
          </div>
          <div className="topbar-right">
            <div className="user-chip">
              <div className="user-avatar">{initials}</div>
              <div>
                <div className="user-chip-name">{user?.username || "Operator"}</div>
              </div>
            </div>
            <button className="btn btn-ghost btn-icon" onClick={logout} title="Sign out" aria-label="Sign out">
              <IconLogout width={17} height={17} />
            </button>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
