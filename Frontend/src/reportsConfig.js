// Every analytics/report endpoint exposed by the backend, driving the
// sidebar submenu and the generic report viewer page.
//
// filter: "period"      -> today/week/month/year/all selector
// filter: "date-range"  -> start_date / end_date pickers
// filter: null           -> no query params, just fetch on load

const reports = [
  { slug: "sales", title: "Sales Report", endpoint: "/orders/api/reports/sales/", filter: "period", group: "Sales" },
  { slug: "date-range-sales", title: "Sales by Date Range", endpoint: "/orders/api/reports/sales/date-range/", filter: "date-range", group: "Sales" },
  { slug: "daily-sales-trend", title: "Daily Sales Trend", endpoint: "/orders/api/reports/daily-sales-trend/", filter: "period", group: "Sales" },
  { slug: "sales-growth", title: "Sales Growth", endpoint: "/orders/api/reports/sales-growth/", filter: "period", group: "Sales" },
  { slug: "top-selling-products", title: "Top Selling Products", endpoint: "/orders/api/reports/top-products/", filter: "period", group: "Sales" },
  { slug: "product-sales-detail", title: "Product Sales Detail", endpoint: "/orders/api/reports/product-sales-detail/", filter: "period", group: "Sales" },
  { slug: "product-performance", title: "Product Performance", endpoint: "/orders/api/reports/product-performance/", filter: "period", group: "Sales" },
  { slug: "product-profit", title: "Product Profit Report", endpoint: "/orders/api/reports/product-profit/", filter: "period", group: "Sales" },

  { slug: "order-status-summary", title: "Order Status Summary", endpoint: "/orders/api/reports/order-status-summary/", filter: null, group: "Orders" },
  { slug: "order-analytics", title: "Order Analytics", endpoint: "/orders/api/reports/order-analytics/", filter: "period", group: "Orders" },
  { slug: "payment-summary", title: "Payment Summary", endpoint: "/orders/api/reports/payment-summary/", filter: "period", group: "Orders" },
  { slug: "financial-summary", title: "Financial Summary", endpoint: "/orders/api/reports/financial-summary/", filter: "period", group: "Orders" },

  { slug: "customer-revenue", title: "Customer Revenue", endpoint: "/orders/api/reports/customer-revenue/", filter: "period", group: "Customers" },
  { slug: "customer-performance", title: "Customer Performance", endpoint: "/orders/api/reports/customer-performance/", filter: "period", group: "Customers" },
  { slug: "customer-analytics", title: "Customer Analytics", endpoint: "/orders/api/reports/customer-analytics/", filter: "period", group: "Customers" },

  { slug: "category-revenue", title: "Category Revenue", endpoint: "/orders/api/reports/category-revenue/", filter: "period", group: "Inventory" },
  { slug: "inventory-sales-performance", title: "Inventory Sales Performance", endpoint: "/orders/api/reports/inventory-sales-performance/", filter: "period", group: "Inventory" },
  { slug: "inventory-movement", title: "Inventory Movement", endpoint: "/orders/api/reports/inventory-movement/", filter: "period", group: "Inventory" },
  { slug: "inventory-valuation", title: "Inventory Valuation", endpoint: "/orders/api/reports/inventory-valuation/", filter: null, group: "Inventory" },
  { slug: "inventory-health", title: "Inventory Health", endpoint: "/orders/api/reports/inventory-health/", filter: null, group: "Inventory" },
  { slug: "inventory-activity", title: "Inventory Activity", endpoint: "/orders/api/reports/inventory-activity/", filter: "period", group: "Inventory" },
  { slug: "low-stock-report", title: "Low Stock Report", endpoint: "/orders/api/reports/low-stock/", filter: null, group: "Inventory" },
  { slug: "supplier-performance", title: "Supplier Performance", endpoint: "/orders/api/reports/supplier-performance/", filter: "period", group: "Inventory" },

  { slug: "dashboard-summary", title: "Dashboard Summary", endpoint: "/orders/api/reports/dashboard-summary/", filter: "period", group: "Overview" },
];

export const REPORT_GROUPS = ["Overview", "Sales", "Orders", "Customers", "Inventory"];

export function reportBySlug(slug) {
  return reports.find((r) => r.slug === slug);
}

export default reports;
