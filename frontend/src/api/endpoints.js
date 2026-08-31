import api from "./client";

// DRF's PageNumberPagination has a fixed PAGE_SIZE and no page_size override
// configured on the backend, so dropdown sources (categories, suppliers,
// customers, products) need to walk every page to be complete.
export async function fetchAllPages(requestFn, maxPages = 20) {
  let page = 1;
  let all = [];
  while (page <= maxPages) {
    const res = await requestFn({ page });
    const data = res.data;
    const results = data.results ?? data;
    all = all.concat(results);
    if (!data.next) break;
    page += 1;
  }
  return all;
}

/* ---------------- Inventory: categories / suppliers / products ---------------- */

export const CategoriesAPI = {
  list: (params) => api.get("/api/categories/", { params }),
  create: (data) => api.post("/api/categories/", data),
  update: (id, data) => api.patch(`/api/categories/${id}/`, data),
  remove: (id) => api.delete(`/api/categories/${id}/`),
};

export const SuppliersAPI = {
  list: (params) => api.get("/api/suppliers/", { params }),
  create: (data) => api.post("/api/suppliers/", data),
  update: (id, data) => api.patch(`/api/suppliers/${id}/`, data),
  remove: (id) => api.delete(`/api/suppliers/${id}/`),
};

export const ProductsAPI = {
  list: (params) => api.get("/api/products/", { params }),
  create: (data) => api.post("/api/products/", data),
  update: (id, data) => api.patch(`/api/products/${id}/`, data),
  remove: (id) => api.delete(`/api/products/${id}/`),
};

export const TransactionsAPI = {
  list: (params) => api.get("/api/transactions/", { params }),
  stockIn: (data) => api.post("/api/stock/in/", data),
  stockOut: (data) => api.post("/api/stock/out/", data),
};

export const InventoryDashboardAPI = {
  summary: () => api.get("/api/dashboard/"),
  lowStock: (params) => api.get("/api/stock/low/", { params }),
  outOfStock: (params) => api.get("/api/stock/out-of-stock/", { params }),
};

/* ---------------- Order management: customers / orders ---------------- */

export const CustomersAPI = {
  list: (params) => api.get("/orders/api/customers/", { params }),
  create: (data) => api.post("/orders/api/customers/", data),
  update: (id, data) => api.patch(`/orders/api/customers/${id}/`, data),
  remove: (id) => api.delete(`/orders/api/customers/${id}/`),
};

export const OrdersAPI = {
  list: (params) => api.get("/orders/api/orders/", { params }),
  detail: (id) => api.get(`/orders/api/orders/${id}/detail/`),
  create: (data) => api.post("/orders/api/orders/", data),
  updateStatus: (id, status) => api.patch(`/orders/api/orders/${id}/status/`, { status }),
  updatePayment: (id, payment_status) => api.patch(`/orders/api/orders/${id}/payment/`, { payment_status }),
  cancel: (id) => api.post(`/orders/api/orders/${id}/cancel/`),
};

export default api;
