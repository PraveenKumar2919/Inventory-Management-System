import { useEffect } from "react";
import { IconX, IconAlert, IconBox, IconTrash } from "./Icons";

/* ---------------------------------------------------------
   Modal
--------------------------------------------------------- */
export function Modal({ title, onClose, children, footer, size = "md" }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="modal-scrim" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className={`modal ${size === "lg" ? "modal-lg" : ""}`}>
        <div className="modal-head">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <IconX width={18} height={18} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------
   Confirm dialog (delete etc.)
--------------------------------------------------------- */
export function ConfirmDialog({ title = "Are you sure?", body, confirmLabel = "Delete", danger = true, onConfirm, onClose, loading }) {
  return (
    <Modal
      title={title}
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className={`btn ${danger ? "btn-danger" : "btn-primary"}`} onClick={onConfirm} disabled={loading}>
            {danger ? <IconTrash width={14} height={14} /> : null}
            {loading ? "Working…" : confirmLabel}
          </button>
        </>
      }
    >
      <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
        <IconAlert width={20} height={20} style={{ color: "var(--alert-red)", flexShrink: 0 }} />
        <p style={{ margin: 0, fontSize: 13.5, color: "var(--text-secondary)" }}>{body}</p>
      </div>
    </Modal>
  );
}

/* ---------------------------------------------------------
   Status stamp badge
--------------------------------------------------------- */
const STAMP_COLORS = {
  // order status
  PENDING: "amber",
  CONFIRMED: "blue",
  PROCESSING: "blue",
  SHIPPED: "blue",
  DELIVERED: "green",
  CANCELLED: "red",
  // payment status
  PAID: "green",
  FAILED: "red",
  REFUNDED: "slate",
  // generic
  ACTIVE: "green",
  INACTIVE: "slate",
  IN: "green",
  OUT: "amber",
  ADJUSTMENT: "blue",
  RETURN: "slate",
  LOW: "amber",
  OK: "green",
};

export function Stamp({ value, labelOverride }) {
  if (value === null || value === undefined || value === "") return <span className="cell-muted">—</span>;
  const key = String(value).toUpperCase();
  const color = STAMP_COLORS[key] || "slate";
  return <span className={`stamp stamp-${color}`}>{labelOverride || String(value).replace(/_/g, " ")}</span>;
}

export function BoolStamp({ value, trueLabel = "Yes", falseLabel = "No" }) {
  return <span className={`stamp stamp-${value ? "green" : "slate"}`}>{value ? trueLabel : falseLabel}</span>;
}

/* ---------------------------------------------------------
   Empty state / loading
--------------------------------------------------------- */
export function EmptyState({ title = "Nothing here yet", body, icon: Icon = IconBox }) {
  return (
    <div className="empty-state">
      <Icon className="em-icon" />
      <h4>{title}</h4>
      {body && <p>{body}</p>}
    </div>
  );
}

export function LoadingRow({ label = "Loading…" }) {
  return <div className="loading-row">{label}</div>;
}

export function Banner({ type = "error", children }) {
  return (
    <div className={`banner banner-${type}`}>
      <IconAlert width={15} height={15} />
      <div>{children}</div>
    </div>
  );
}

/* ---------------------------------------------------------
   Pagination footer (DRF PageNumberPagination shape)
--------------------------------------------------------- */
export function Pagination({ count, page, pageSize = 10, onPage }) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  if (totalPages <= 1) return null;
  return (
    <div className="pagination">
      <span>
        Page {page} of {totalPages} · {count} total
      </span>
      <div style={{ display: "flex", gap: 6 }}>
        <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => onPage(page - 1)}>
          Prev
        </button>
        <button className="btn btn-secondary btn-sm" disabled={page >= totalPages} onClick={() => onPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}
