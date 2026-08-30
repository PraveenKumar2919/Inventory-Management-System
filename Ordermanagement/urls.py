from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerList,
    CustomerAdd,
    CustomerDelete,
    CustomerUpdate,
    CustomerViewSet,
    OrderViewSet,
    OrderDetailView,
    OrderStatusUpdateView,
    PaymentStatusUpdateView,
    CancelOrderView,
    SalesReportView,
    TopSellingProductsView,
    CustomerRevenueReportView,
    CategoryRevenueReportView,
    PaymentSummaryReportView,
    OrderStatusSummaryReportView,
    InventorySalesPerformanceView,
    LowStockReportView,
    DashboardSummaryView,
    DateRangeSalesReportView,
    ProductProfitReportView,
    SupplierPerformanceReportView,
    InventoryMovementReportView,
    ProductSalesDetailReportView,
    DailySalesTrendView,
    ProductPerformanceReportView,
    FinancialSummaryReportView,
    CustomerPerformanceReportView,
    InventoryValuationReportView,
    OrderAnalyticsReportView,
    SalesGrowthReportView,
    CustomerAnalyticsReportView,
    InventoryHealthReportView,
    InventoryActivityReportView,
    SalesAnalyticsView,
)


# =========================================================
# REST API ROUTER
# =========================================================

router = DefaultRouter()

router.register(
    "customers",
    CustomerViewSet,
    basename="customers"
)

router.register(
    "orders",
    OrderViewSet,
    basename="orders"
)


urlpatterns = [

    # =====================================================
    # EXISTING HTML CUSTOMER URLs
    # =====================================================

    path(
        "all/customers/",
        CustomerList,
        name="customer-list"
    ),

    path(
        "add/customer/",
        CustomerAdd,
        name="customer-add"
    ),

    path(
        "delete/customer/<int:id>/",
        CustomerDelete,
        name="customer-delete"
    ),

    path(
        "update/customer/<int:id>/",
        CustomerUpdate,
        name="customer-update"
    ),


    # =====================================================
    # REST API ROUTES
    # =====================================================

    path(
        "api/",
        include(router.urls)
    ),


    # =====================================================
    # ORDER DETAIL
    # =====================================================

    path(
        "api/orders/<int:pk>/detail/",
        OrderDetailView.as_view(),
        name="order-detail"
    ),


    # =====================================================
    # ORDER STATUS
    # =====================================================

    path(
        "api/orders/<int:pk>/status/",
        OrderStatusUpdateView.as_view(),
        name="order-status-update"
    ),


    # =====================================================
    # PAYMENT STATUS
    # =====================================================

    path(
        "api/orders/<int:pk>/payment/",
        PaymentStatusUpdateView.as_view(),
        name="payment-status-update"
    ),


    # =====================================================
    # CANCEL ORDER
    # =====================================================

    path(
        "api/orders/<int:pk>/cancel/",
        CancelOrderView.as_view(),
        name="order-cancel"
    ),

    # =====================================================
    # SALES REPORT
    # =====================================================

    path(
        "api/reports/sales/",
        SalesReportView.as_view(),
        name="sales-report"
    ),

    # =====================================================
    # TOP SELLING PRODUCTS
    # =====================================================

    path(
        "api/reports/top-products/",
        TopSellingProductsView.as_view(),
        name="top-selling-products"
    ),

# =====================================================
# CUSTOMER REVENUE REPORT
# =====================================================

    path(
        "api/reports/customer-revenue/",
        CustomerRevenueReportView.as_view(),
        name="customer-revenue-report"
    ),

# =====================================================
# CATEGORY REVENUE REPORT
# =====================================================

    path(
        "api/reports/category-revenue/",
        CategoryRevenueReportView.as_view(),
        name="category-revenue-report"
    ),
# =====================================================
# PAYMENT SUMMARY REPORT
# =====================================================

    path(
        "api/reports/payment-summary/",
        PaymentSummaryReportView.as_view(),
        name="payment-summary-report"
    ),
# =====================================================
# ORDER STATUS SUMMARY REPORT
# =====================================================

    path(
        "api/reports/order-status-summary/",
        OrderStatusSummaryReportView.as_view(),
        name="order-status-summary-report"
    ),
# =====================================================
# INVENTORY SALES PERFORMANCE
# =====================================================

    path(
        "api/reports/inventory-sales-performance/",
        InventorySalesPerformanceView.as_view(),
        name="inventory-sales-performance"
    ),
# =====================================================
# LOW STOCK REPORT
# =====================================================

    path(
        "api/reports/low-stock/",
        LowStockReportView.as_view(),
        name="low-stock-report"
    ),
# =====================================================
# DASHBOARD SUMMARY
# =====================================================

    path(
        "api/reports/dashboard-summary/",
        DashboardSummaryView.as_view(),
        name="dashboard-summary"
    ),

# =====================================================
# DATE RANGE SALES REPORT
# =====================================================

    path(
        "api/reports/sales/date-range/",
        DateRangeSalesReportView.as_view(),
        name="date-range-sales-report"
    ),
# =====================================================
# PRODUCT PROFIT REPORT
# =====================================================

    path(
        "api/reports/product-profit/",
        ProductProfitReportView.as_view(),
        name="product-profit-report"
    ),

# =====================================================
# SUPPLIER PERFORMANCE REPORT
# =====================================================

    path(
        "api/reports/supplier-performance/",
        SupplierPerformanceReportView.as_view(),
        name="supplier-performance-report"
    ),
# =====================================================
# INVENTORY MOVEMENT REPORT
# =====================================================

    path(
        "api/reports/inventory-movement/",
        InventoryMovementReportView.as_view(),
        name="inventory-movement-report"
    ),


# =====================================================
# PRODUCT SALES DETAIL REPORT
# =====================================================
    path(
        "api/reports/product-sales-detail/",
        ProductSalesDetailReportView.as_view(),
        name="product-sales-detail"
    ),

# =====================================================
# DAILY SALES TREND
# =====================================================
    path(
        "api/reports/daily-sales-trend/",
        DailySalesTrendView.as_view(),
        name="daily-sales-trend"
    ),

# =====================================================
# PRODUCT PERFORMANCE REPORT
# =====================================================

    path(
        "api/reports/product-performance/",
        ProductPerformanceReportView.as_view(),
        name="product-performance"
    ),

# =====================================================
# Financial Summary Report
# =====================================================

    path(
        "api/reports/financial-summary/",
        FinancialSummaryReportView.as_view(),
        name="financial-summary",
    ),

# =====================================================
# Customer Performance Report
# =====================================================

    path(
        "api/reports/customer-performance/",
        CustomerPerformanceReportView.as_view(),
        name="customer-performance",
    ),

# =====================================================
# Inventory Valuation Report
# =====================================================


    path(
        "api/reports/inventory-valuation/",
        InventoryValuationReportView.as_view(),
        name="inventory-valuation",
    ),

# =====================================================
# Order Analytics Report
# =====================================================

    path(
        "api/reports/order-analytics/",
            OrderAnalyticsReportView.as_view(),
        name="order-analytics",
    ),

# =====================================================
# Sales Growth Report
# =====================================================


    path(
        "api/reports/sales-growth/",
        SalesGrowthReportView.as_view(),
        name="sales-growth",
    ),

# =====================================================
# Customer Analytics Report
# =====================================================

    path(
        "api/reports/customer-analytics/",
        CustomerAnalyticsReportView.as_view(),
        name="customer-analytics",
    ),
# =====================================================
# Customer Analytics Report
# =====================================================
    path(
        "api/reports/inventory-health/",
        InventoryHealthReportView.as_view(),
        name="inventory-health",
    ),

# =====================================================
# Inventory Activity Report
# =====================================================
    path(
        "api/reports/inventory-activity/",
        InventoryActivityReportView.as_view(),
        name="inventory-activity",
    ),

    # =====================================================
    # SalesAnalytics
    # =====================================================
    path(
        "api/reports/sales/7-days/",
        SalesAnalyticsView.as_view(),
        name="sales-analytics"
    ),

]