import { createContext, useContext, useEffect, useState, useCallback } from "react";
import axios from "axios";
import api, { API_BASE_URL, tokenStore, apiErrorMessage } from "../api/client";

const AuthContext = createContext(null);

function decodeJwt(token) {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decodeURIComponent(escape(json)));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const access = tokenStore.getAccess();
    if (access) {
      const payload = decodeJwt(access);
      setUser(payload ? { username: payload.username || `Operator #${payload.user_id ?? ""}` } : { username: "Operator" });
    }
    setReady(true);
  }, []);

  const login = useCallback(async (username, password) => {
    const res = await axios.post(`${API_BASE_URL}/api/auth/token/`, {
      username,
      password,
    });
    tokenStore.set(res.data.access, res.data.refresh);
    const payload = decodeJwt(res.data.access);
    setUser(payload ? { username: payload.username || username } : { username });
    return true;
  }, []);

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
    window.location.href = "/login";
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export { apiErrorMessage };
export default api;
