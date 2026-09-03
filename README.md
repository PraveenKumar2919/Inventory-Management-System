# 📦 Inventory Management System

A full-stack **Inventory Management System** built with **Django REST Framework** and **React (Vite)**.

The application provides inventory management, stock tracking, customer and order management, sales analytics, JWT authentication, and RESTful APIs with Swagger documentation.

## 🚀 Live Demo

**Frontend:**
https://inventory-management-system-henna-xi.vercel.app

**API Documentation:**
https://inventory-management-system-lgz8.onrender.com/api/docs/

> **Note:** The backend is hosted on Render's free tier. The first request after a period of inactivity may take a few seconds while the service wakes up.

---

## ✨ Features

### 🔐 Authentication

* JWT-based authentication
* Access and refresh token support
* Protected frontend routes
* Secure API access

### 📦 Inventory Management

* Product management
* Category management
* Supplier management
* Stock In / Stock Out
* Low-stock alerts
* Out-of-stock tracking
* Inventory transaction history

### 🛒 Order Management

* Customer management
* Order creation and management
* Order status tracking
* Payment status tracking
* Order cancellation

### 📊 Reports & Analytics

* Sales reports
* Revenue analysis
* Profit analysis
* Inventory valuation
* Customer performance
* Supplier performance
* Stock analytics
* Reporting and analytics endpoints

### 📚 API Documentation

* RESTful API architecture
* OpenAPI schema
* Swagger UI
* Request and response documentation

---

## 🛠️ Tech Stack

### Backend

* Python
* Django 5.2
* Django REST Framework
* SimpleJWT
* django-filter
* drf-spectacular
* SQLite
* PostgreSQL-ready
* Gunicorn
* Render

### Frontend

* React 19
* Vite
* React Router
* Axios
* Recharts
* Vercel

### Development Tools

* Git
* GitHub
* Postman
* Swagger UI
* PyCharm / VS Code

---

## 🏗️ Project Structure

```text
PythonProject/
│
├── Backend/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── Inventary/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── Ordermanagement/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   └── pages/
│   │
│   ├── package.json
│   └── vite.config.js
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🔗 API Overview

| Module         | Endpoint                   |
| -------------- | -------------------------- |
| Authentication | `/api/auth/token/`         |
| Token Refresh  | `/api/auth/token/refresh/` |
| Products       | `/api/products/`           |
| Categories     | `/api/categories/`         |
| Suppliers      | `/api/suppliers/`          |
| Transactions   | `/api/transactions/`       |
| Stock In       | `/api/stock/in/`           |
| Stock Out      | `/api/stock/out/`          |
| Customers      | `/orders/api/customers/`   |
| Orders         | `/orders/api/orders/`      |
| Reports        | `/orders/api/reports/...`  |
| Swagger        | `/api/docs/`               |
| OpenAPI Schema | `/api/schema/`             |

For complete API documentation, visit the Swagger UI.

---

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/PraveenKumar2919/Inventory-Management-System.git
cd Inventory-Management-System
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

**Windows:**

```powershell
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

### 6. Start Django Server

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

---

## 💻 Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
```

Create `.env`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the React development server:

```powershell
npm run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

---

## 🌐 Deployment

### Backend

The Django REST API is deployed on **Render**.

### Frontend

The React application is deployed on **Vercel**.

---

## 🔒 Environment Variables

### Backend

```text
DEBUG
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
```

### Frontend

```text
VITE_API_BASE_URL
```

> Never commit passwords, secret keys, API keys, database credentials, or other sensitive information to GitHub.

---

## 📸 Screenshots

Screenshots of the following modules can be added:

* Dashboard
* Products
* Inventory
* Customers
* Orders
* Reports
* Analytics

---

## 👨‍💻 Author

**Praveen Kumar**

GitHub:
https://github.com/PraveenKumar2919

Portfolio:
https://praveenkumar2919.github.io/Portfolio/

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
