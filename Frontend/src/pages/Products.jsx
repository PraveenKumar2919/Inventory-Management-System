import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ProductsAPI, CategoriesAPI, SuppliersAPI, fetchAllPages } from "../api/endpoints";
import { apiErrorMessage } from "../api/client";
import { useToast } from "../context/ToastContext";
import { Modal, ConfirmDialog, LoadingRow, EmptyState, Banner, BoolStamp, Pagination } from "../components/Kit";
import { IconPlus, IconEdit, IconTrash, IconBox, IconSearch } from "../components/Icons";

const emptyForm = {
  product_name: "",
  product_code: "",
  category: "",
  supplier: "",
  description: "",
  cost_price: "0.00",
  selling_price: "0.00",
  gst: "0.00",
  quantity: 0,
  minimum_stock: 10,
  maximum_stock: 100,
  unit: "piece",
  expiry_date: "",
  food_product: false,
  is_active: true,
};

const money = (v) => `₹${Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;

export default function Products() {
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const stockFilter = searchParams.get("stock") || ""; // low | out | ""

  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  const [modal, setModal] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchAllPages((p) => CategoriesAPI.list(p)).then(setCategories).catch(() => {});
    fetchAllPages((p) => SuppliersAPI.list(p)).then(setSuppliers).catch(() => {});
  }, []);

  function load() {
    setLoading(true);
    setError("");
    const params = { page, search: search || undefined, category: categoryFilter || undefined };
    if (stockFilter === "low") params.is_low_stock = true; // best-effort hint; falls back to client filter below
    ProductsAPI.list(params)
      .then((res) => {
        const d = res.data;
        let results = d.results ?? d;
        if (stockFilter === "low") results = results.filter((p) => p.is_low_stock);
        if (stockFilter === "out") results = results.filter((p) => p.is_out_of_stock);
        setItems(results);
        setCount(stockFilter ? results.length : d.count ?? results.length);
      })
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load products.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, [page, categoryFilter, stockFilter]);

  function openCreate() {
    setForm(emptyForm);
    setFormError("");
    setModal("create");
  }
  function openEdit(item) {
    setForm({
      product_name: item.product_name,
      product_code: item.product_code,
      category: item.category || "",
      supplier: item.supplier || "",
      description: item.description || "",
      cost_price: item.cost_price,
      selling_price: item.selling_price,
      gst: item.gst,
      quantity: item.quantity,
      minimum_stock: item.minimum_stock,
      maximum_stock: item.maximum_stock,
      unit: item.unit,
      expiry_date: item.expiry_date || "",
      food_product: item.food_product,
      is_active: item.is_active,
    });
    setFormError("");
    setModal({ mode: "edit", id: item.id });
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setFormError("");
    const payload = {
      ...form,
      category: form.category || null,
      supplier: form.supplier || null,
      expiry_date: form.expiry_date || null,
    };
    try {
      if (modal === "create") {
        await ProductsAPI.create(payload);
        toast.success("Product added.");
      } else {
        await ProductsAPI.update(modal.id, payload);
        toast.success("Product updated.");
      }
      setModal(null);
      load();
    } catch (err) {
      setFormError(apiErrorMessage(err, "Couldn't save this product."));
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    setDeleting(true);
    try {
      await ProductsAPI.remove(deleteTarget.id);
      toast.success("Product deleted.");
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Couldn't delete this product."));
    } finally {
      setDeleting(false);
    }
  }

  const filterLabel = useMemo(() => {
    if (stockFilter === "low") return "Low stock";
    if (stockFilter === "out") return "Out of stock";
    return "";
  }, [stockFilter]);

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Inventory</div>
          <h1 className="page-title">Products</h1>
          <p className="page-desc">Every SKU on the shelf — pricing, GST, stock thresholds and supplier links.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-primary" onClick={openCreate}>
            <IconPlus /> Add product
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrap">
          <IconSearch />
          <input
            placeholder="Search name or code…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (setPage(1), load())}
          />
        </div>
        <select value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <button className="btn btn-secondary btn-sm" onClick={() => (setPage(1), load())}>Search</button>
        {filterLabel && (
          <span className="pill-count" style={{ display: "flex", alignItems: "center", gap: 6 }}>
            {filterLabel}
            <button className="btn-ghost" style={{ border: "none", background: "none", cursor: "pointer", padding: 0, color: "inherit" }} onClick={() => setSearchParams({})}>✕</button>
          </span>
        )}
      </div>

      {error && <Banner type="error">{error}</Banner>}

      <div className="panel">
        <div className="table-wrap">
          {loading ? (
            <LoadingRow />
          ) : items.length === 0 ? (
            <EmptyState icon={IconBox} title="No products found" body="Try a different search or add a new product." />
          ) : (
            <table className="manifest">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>GST</th>
                  <th>Stock</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <div className="cell-strong">{p.product_name}</div>
                      <div className="cell-code">{p.product_code}</div>
                    </td>
                    <td className="cell-muted">{p.category_name || "—"}</td>
                    <td className="cell-num">{money(p.selling_price)}</td>
                    <td className="cell-num">{p.gst}%</td>
                    <td>
                      <span className="mono">{p.quantity} {p.unit}</span>
                      {p.is_out_of_stock ? <div className="stamp stamp-red" style={{ marginTop: 4 }}>Out</div>
                        : p.is_low_stock ? <div className="stamp stamp-amber" style={{ marginTop: 4 }}>Low</div> : null}
                    </td>
                    <td><BoolStamp value={p.is_active} trueLabel="Active" falseLabel="Inactive" /></td>
                    <td>
                      <div className="row-actions">
                        <button className="btn btn-secondary btn-sm btn-icon" onClick={() => openEdit(p)} aria-label="Edit"><IconEdit width={14} height={14} /></button>
                        <button className="btn btn-danger btn-sm btn-icon" onClick={() => setDeleteTarget(p)} aria-label="Delete"><IconTrash width={14} height={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        {!stockFilter && <Pagination count={count} page={page} onPage={setPage} />}
      </div>

      {modal && (
        <Modal
          size="lg"
          title={modal === "create" ? "Add product" : "Edit product"}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" form="product-form" type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save product"}
              </button>
            </>
          }
        >
          {formError && <Banner type="error">{formError}</Banner>}
          <form id="product-form" onSubmit={submit}>
            <div className="field-row">
              <div className="field">
                <label>Product name</label>
                <input required value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })} />
              </div>
              <div className="field">
                <label>Product code (SKU)</label>
                <input required value={form.product_code} onChange={(e) => setForm({ ...form, product_code: e.target.value })} />
              </div>
            </div>

            <div className="field-row">
              <div className="field">
                <label>Category</label>
                <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                  <option value="">— None —</option>
                  {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Supplier</label>
                <select value={form.supplier} onChange={(e) => setForm({ ...form, supplier: e.target.value })}>
                  <option value="">— None —</option>
                  {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
            </div>

            <div className="field">
              <label>Description</label>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>

            <div className="field-row">
              <div className="field">
                <label>Cost price</label>
                <input type="number" step="0.01" min="0" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })} />
              </div>
              <div className="field">
                <label>Selling price</label>
                <input type="number" step="0.01" min="0" required value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })} />
              </div>
            </div>

            <div className="field-row">
              <div className="field">
                <label>GST %</label>
                <input type="number" step="0.01" min="0" value={form.gst} onChange={(e) => setForm({ ...form, gst: e.target.value })} />
              </div>
              <div className="field">
                <label>Unit</label>
                <input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} placeholder="piece, kg, box…" />
              </div>
            </div>

            <div className="field-row">
              <div className="field">
                <label>Quantity on hand</label>
                <input type="number" min="0" required value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
              </div>
              <div className="field">
                <label>Expiry date</label>
                <input type="date" value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} />
              </div>
            </div>

            <div className="field-row">
              <div className="field">
                <label>Minimum stock</label>
                <input type="number" min="0" value={form.minimum_stock} onChange={(e) => setForm({ ...form, minimum_stock: e.target.value })} />
              </div>
              <div className="field">
                <label>Maximum stock</label>
                <input type="number" min="0" value={form.maximum_stock} onChange={(e) => setForm({ ...form, maximum_stock: e.target.value })} />
              </div>
            </div>

            <div style={{ display: "flex", gap: 20 }}>
              <div className="checkbox-row">
                <input type="checkbox" id="p-food" checked={form.food_product} onChange={(e) => setForm({ ...form, food_product: e.target.checked })} />
                <label htmlFor="p-food" style={{ margin: 0 }}>Food product</label>
              </div>
              <div className="checkbox-row">
                <input type="checkbox" id="p-active" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
                <label htmlFor="p-active" style={{ margin: 0 }}>Active</label>
              </div>
            </div>
          </form>
        </Modal>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete product"
          body={`Delete "${deleteTarget.product_name}" (${deleteTarget.product_code})? This can't be undone.`}
          onConfirm={confirmDelete}
          onClose={() => setDeleteTarget(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}
