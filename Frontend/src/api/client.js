import axios from "axios";

// Base URL of the Django backend. Configure via .env -> VITE_API_BASE_URL
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const ACCESS_KEY = "consign_access_token";
const REFRESH_KEY = "consign_refresh_token";

export const tokenStore = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  set: (access, refresh) => {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = tokenStore.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let queue = [];

function flushQueue(error, token) {
  queue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  queue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;

    if (
      error.response &&
      error.response.status === 401 &&
      !original._retry &&
      tokenStore.getRefresh()
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject });
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          return api(original);
        });
      }

      original._retry = true;
      isRefreshing = true;

      try {
        const res = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh: tokenStore.getRefresh(),
        });
        const newAccess = res.data.access;
        tokenStore.set(newAccess, null);
        flushQueue(null, newAccess);
        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (refreshErr) {
        flushQueue(refreshErr, null);
        tokenStore.clear();
        window.location.href = "/login";
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Pulls a readable message out of a DRF error response.
export function apiErrorMessage(err, fallback = "Something went wrong.") {
  const data = err?.response?.data;
  if (!data) return err?.message || fallback;
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  if (data.message) return data.message;

  // Field-level validation errors -> flatten into one line
  try {
    const parts = [];
    Object.entries(data).forEach(([key, val]) => {
      const msg = Array.isArray(val) ? val.join(" ") : String(val);
      parts.push(key === "non_field_errors" ? msg : `${key}: ${msg}`);
    });
    if (parts.length) return parts.join(" · ");
  } catch {
    /* noop */
  }
  return fallback;
}

export default api;
