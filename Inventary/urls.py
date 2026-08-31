from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    SupplierViewSet,
    ProductViewSet,
    InventoryTransactionListView,
    StockInView,
    StockOutView,
    DashboardView,
    LowStockProductsView,
    OutOfStockProductsView,
)


router = DefaultRouter()


# =========================================================
# CATEGORY
# =========================================================

router.register(
    r"categories",
    CategoryViewSet,
    basename="categories"
)


# =========================================================
# SUPPLIER
# =========================================================

router.register(
    r"suppliers",
    SupplierViewSet,
    basename="suppliers"
)


# =========================================================
# PRODUCT
# =========================================================

router.register(
    r"products",
    ProductViewSet,
    basename="products"
)


urlpatterns = [

    # Router
    path(
        "",
        include(router.urls)
    ),

    # Transactions
    path(
        "transactions/",
        InventoryTransactionListView.as_view(),
        name="transactions"
    ),

    # Stock In
    path(
        "stock/in/",
        StockInView.as_view(),
        name="stock-in"
    ),

    # Stock Out
    path(
        "stock/out/",
        StockOutView.as_view(),
        name="stock-out"
    ),

    # Dashboard
    path(
        "dashboard/",
        DashboardView.as_view(),
        name="dashboard"
    ),
    # Low Stock
    path(
        "stock/low/",
        LowStockProductsView.as_view(),
        name="low-stock"
    ),

    # Out Of Stock
    path(
        "stock/out-of-stock/",
        OutOfStockProductsView.as_view(),
        name="out-of-stock"
    ),
]