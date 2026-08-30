import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import Categories from "./pages/Categories";
import Suppliers from "./pages/Suppliers";
import Transactions from "./pages/Transactions";
import Customers from "./pages/Customers";
import OrdersList from "./pages/OrdersList";
import OrderCreate from "./pages/OrderCreate";
import OrderDetail from "./pages/OrderDetail";
import ReportsIndex from "./pages/ReportsIndex";
import ReportView from "./pages/ReportView";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<Login />} />

            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/products" element={<Products />} />
              <Route path="/categories" element={<Categories />} />
              <Route path="/suppliers" element={<Suppliers />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/orders" element={<OrdersList />} />
              <Route path="/orders/new" element={<OrderCreate />} />
              <Route path="/orders/:id" element={<OrderDetail />} />
              <Route path="/reports" element={<ReportsIndex />} />
              <Route path="/reports/:slug" element={<ReportView />} />
            </Route>

            <Route path="*" element={<Dashboard />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
