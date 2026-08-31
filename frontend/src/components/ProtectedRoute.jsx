import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LoadingRow } from "./Kit";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, ready } = useAuth();
  const location = useLocation();

  if (!ready) return <LoadingRow label="Checking session…" />;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
}
