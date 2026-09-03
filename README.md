\# Inventory Management System



A full-stack inventory, order, and sales-reporting platform built with \*\*Django REST Framework\*\* on the backend and \*\*React (Vite)\*\* on the frontend. Includes JWT authentication, stock tracking, order management, and 25+ analytics/reporting endpoints.



\*\*Live demo:\*\* \[inventory-management-system-henna-xi.vercel.app](https://inventory-management-system-henna-xi.vercel.app)

\*\*API docs (Swagger):\*\* \[inventory-management-system-lgz8.onrender.com/api/docs/](https://inventory-management-system-lgz8.onrender.com/api/docs/)



> Note: the backend runs on Render's free tier, so the first request after inactivity may take 10-30 seconds to wake up.



\---



\## Features



\- \*\*Authentication\*\* — JWT-based login with access/refresh token flow and protected frontend routes

\- \*\*Inventory management\*\* — categories, suppliers, products, stock in/out, low-stock \& out-of-stock alerts

\- \*\*Order management\*\* — customers, orders, order status \& payment status tracking, order cancellation

\- \*\*Reporting \& analytics\*\* — sales, revenue, profit, inventory valuation, customer/supplier performance, and more (25+ report endpoints)

\- \*\*API documentation\*\* — auto-generated OpenAPI schema with Swagger UI (via `drf-spectacular`)



\## Tech Stack



\*\*Backend\*\*

\- Django 5.2, Django REST Framework

\- SimpleJWT (authentication)

\- django-filter, drf-spectacular

\- SQLite (dev) / PostgreSQL-ready

\- Deployed on \[Render](https://render.com)



\*\*Frontend\*\*

\- React 19 + Vite

\- React Router

\- Axios

\- Recharts (data visualization)

\- Deployed on \[Vercel](https://vercel.com)



\## Project Structure



```

PythonProject/

├── Backend/            # Django project settings, root URLs

├── Inventary/          # Products, categories, suppliers, stock transactions

├── Ordermanagement/    # Customers, orders, and reports

├── frontend/           # React (Vite) single-page app

│   └── src/

│       ├── api/        # Axios client \& endpoints

│       ├── context/    # Auth \& toast context providers

│       ├── pages/       # Route-level pages

│       └── components/  # Shared UI components

├── manage.py

└── requirements.txt

```



\## API Overview



| Area | Base path |

|---|---|

| Auth (JWT) | `/api/auth/token/`, `/api/auth/token/refresh/` |

| Inventory | `/api/categories/`, `/api/suppliers/`, `/api/products/`, `/api/transactions/`, `/api/stock/in/`, `/api/stock/out/` |

| Orders | `/orders/api/customers/`, `/orders/api/orders/` |

| Reports | `/orders/api/reports/...` (sales, revenue, profit, inventory valuation, customer/supplier performance, etc.) |

| Docs | `/api/docs/` (Swagger UI), `/api/schema/` (OpenAPI schema) |



Full endpoint list with request/response schemas is available via Swagger.



\## Getting Started (Local Setup)



\### Backend



```bash

\# from the project root

python -m venv .venv

.venv\\Scripts\\activate        # Windows

\# source .venv/bin/activate   # macOS/Linux



pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

```



Backend runs at `http://127.0.0.1:8000`.



\### Frontend



```bash

cd frontend

npm install

cp .env.example .env      # set VITE\_API\_BASE\_URL if needed

npm run dev

```



Frontend runs at `http://127.0.0.1:5173`.



\## Environment Variables



\*\*Backend\*\* (`Backend/settings.py` / environment)

\- `DEBUG`

\- `ALLOWED\_HOSTS`

\- `CORS\_ALLOWED\_ORIGINS`, `CSRF\_TRUSTED\_ORIGINS`



\*\*Frontend\*\* (`frontend/.env`)

\- `VITE\_API\_BASE\_URL` — base URL of the Django backend (e.g. `http://127.0.0.1:8000` locally, or the Render URL in production)



\## Deployment



\- \*\*Backend\*\* is deployed on Render as a Python web service (`gunicorn Backend.wsgi`)

\- \*\*Frontend\*\* is deployed on Vercel with root directory set to `frontend/`



\## Author



\*\*Praveen Kumar\*\*

GitHub: \[@PraveenKumar2919](https://github.com/PraveenKumar2919)

