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
- JWT-based authentication
- Access and refresh token support
- Protected frontend routes
- Secure API access

### 📦 Inventory Management
- Product management
- Category management
- Supplier management
- Stock In / Stock Out
- Low-stock alerts
- Out-of-stock tracking
- Inventory transaction history

### 🛒 Order Management
- Customer management
- Order creation and management
- Order status tracking
- Payment status tracking
- Order cancellation

### 📊 Reports & Analytics
- Sales reports
- Revenue analysis
- Profit analysis
- Inventory valuation
- Customer performance
- Supplier performance
- Stock analytics
- 25+ reporting and analytics endpoints

### 📚 API Documentation
- RESTful API architecture
- OpenAPI schema
- Swagger UI
- Request and response documentation

---

## 🛠️ Tech Stack

### Backend

- Python
- Django 5.2
- Django REST Framework
- SimpleJWT
- django-filter
- drf-spectacular
- SQLite for development
- PostgreSQL-ready
- Gunicorn
- Render

### Frontend

- React 19
- Vite
- React Router
- Axios
- Recharts
- Vercel

### Development Tools

- Git
- GitHub
- VS Code / PyCharm
- Postman
- Swagger UI

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