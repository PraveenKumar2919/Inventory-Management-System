# Consign — Inventory & Order Console (React frontend)

A standalone React (Vite) app that talks to the existing Django REST
Framework backend (`Inventary` + `Ordermanagement`) over JWT-authenticated
API calls. It replaces the old, disconnected Django `Frontend` app templates.

## Run it

```bash
cd frontend
npm install
cp .env.example .env      # point VITE_API_BASE_URL at your Django server
npm run dev                # http://localhost:5173
```

Backend, in a separate terminal:

```bash
pip install -r requirements.txt   # adds django-cors-headers
python manage.py migrate
python manage.py runserver
```

CORS is already configured in `Backend/settings.py` to allow
`http://localhost:5173` and `http://127.0.0.1:5173`. If you serve the
frontend from a different host/port, add it to `CORS_ALLOWED_ORIGINS`.

Sign in with any existing Django user (`python manage.py createsuperuser`
works). Login uses `/api/auth/token/` (SimpleJWT) and silently refreshes
access tokens via `/api/auth/token/refresh/`.

## What's inside

- **Dashboard** — stock value, sales, low/out-of-stock counts, recent orders,
  order pipeline, pulled from `/api/dashboard/`.
- **Products / Categories / Suppliers** — full CRUD against the DRF
  viewsets, with category/stock filters and a low-stock/out-of-stock
  quick link from the dashboard.
- **Transactions** — stock ledger with Stock In / Stock Out forms
  (`/api/stock/in/`, `/api/stock/out/`).
- **Customers** — CRUD against `/orders/api/customers/`.
- **Orders** — list with status/payment filters, a line-item order builder
  that live-computes totals, and an order detail page with guided
  status/payment transitions (mirrors the backend's allowed-transition
  rules) and cancellation.
- **Reports desk** — every one of the 24 analytics endpoints under
  `/orders/api/reports/...` is wired up via `src/reportsConfig.js` and
  rendered through a generic JSON-to-UI renderer
  (`src/components/JsonView.jsx`) that turns scalars into KPI cards,
  arrays of objects into tables, and nested objects into sub-panels —
  so new report endpoints can be added with one config entry.

## Design

"Freight manifest" theme: an ink-navy sidebar, cool paper-gray canvas,
Space Grotesk for headings, Inter for body text, and IBM Plex Mono for
product codes / order numbers / figures. Status badges render as
angled "stamp" chips (`.stamp` in `src/styles/global.css`) — a nod to
warehouse paperwork, and the one deliberately distinctive visual signature
of the whole app.

## Notes

- The old `Frontend` Django app (templates under `Frontend/templates/`)
  is left in place but is no longer wired to working views — its
  `{% url %}` names and context variables had already drifted out of
  sync with the current API-only `Inventary`/`Ordermanagement` views
  before this rebuild. It's safe to remove once you've confirmed
  nothing else references it.
- Report pagination: category/supplier/product/customer dropdowns walk
  every page of the DRF `PageNumberPagination` response (`fetchAllPages`
  in `src/api/endpoints.js`) since the backend doesn't expose a
  `page_size` override.
