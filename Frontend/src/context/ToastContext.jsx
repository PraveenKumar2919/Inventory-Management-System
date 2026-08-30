import { createContext, useCallback, useContext, useRef, useState } from "react";
import { IconCheck, IconAlert, IconInfo } from "../components/Icons";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const push = useCallback((message, type = "info") => {
    const id = ++idRef.current;
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => {
      setToasts((t) => t.filter((x) => x.id !== id));
    }, 3800);
  }, []);

  const api = {
    success: (m) => push(m, "ok"),
    error: (m) => push(m, "err"),
    info: (m) => push(m, "info"),
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast-stack">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>
            {t.type === "ok" && <IconCheck width={14} height={14} />}
            {t.type === "err" && <IconAlert width={14} height={14} />}
            {t.type === "info" && <IconInfo width={14} height={14} />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx;
}
