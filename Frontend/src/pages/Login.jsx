import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Banner } from "../components/Kit";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const from = location.state?.from?.pathname || "/";

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(
        err?.response?.status === 401
          ? "Incorrect username or password."
          : "Couldn't reach the server. Check the API is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-side">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 40 }}>
            <div className="sidebar-brand-mark">C·</div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 17 }}>Consign</div>
          </div>
          <h1 style={{ fontSize: 34, color: "#fff", maxWidth: 460, lineHeight: 1.15 }}>
            One manifest for stock, suppliers and every order in transit.
          </h1>
          <p style={{ color: "var(--text-on-dark-muted)", maxWidth: 420, marginTop: 14, fontSize: 14 }}>
            Sign in with your operator account to reach inventory, order management
            and the full analytics desk.
          </p>
        </div>
        <div className="login-side-manifest">
          MANIFEST — INVENTORY &amp; ORDER CONSOLE<br />
          STOCK · SUPPLIERS · CUSTOMERS · ORDERS<br />
          ACCESS: JWT AUTHENTICATED SESSION
        </div>
      </div>

      <div className="login-form-col">
        <div className="login-card">
          <h2 style={{ fontSize: 21, marginBottom: 4 }}>Sign in</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 13, marginBottom: 22 }}>
            Use your Django account credentials.
          </p>

          {error && <Banner type="error">{error}</Banner>}

          <form onSubmit={onSubmit}>
            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={loading} style={{ marginTop: 6 }}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
