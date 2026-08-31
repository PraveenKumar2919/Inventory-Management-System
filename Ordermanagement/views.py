from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, models
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from .forms import CustomerForm
from decimal import Decimal

from .models import (
    Customer,
    Order,
    OrderItem,
)
from Inventary.models import (
    Product,
    Supplier,
    InventoryTransaction,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from .permissions import (
    IsAdminRole,
    IsStaffRole,
    IsAdminOrStaffReadOnly,
)
from django.db.models import (
    Sum,
    Count,
    F,
    Q,
    ExpressionWrapper,
    DecimalField,
)
from .serializers import (
    CustomerSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
    PaymentStatusUpdateSerializer,
)





# =========================================================
# CUSTOMER - EXISTING HTML CRUD
# =========================================================

def CustomerList(request):

    context = {
        "all_customers": Customer.objects.all()
    }

    return render(
        request,
        "customer.html",
        context
    )


def CustomerAdd(request):

    if request.method == "POST":

        form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("CustomerList")

    else:
        form = CustomerForm()

    return render(
        request,
        "customer_add.html",
        {
            "form": form
        }
    )


def CustomerDelete(request, id):

    customer = get_object_or_404(
        Customer,
        id=id
    )

    customer.delete()

    return redirect("CustomerList")


def CustomerUpdate(request, id):

    customer = get_object_or_404(
        Customer,
        id=id
    )

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():
            form.save()

            return redirect("CustomerList")

    else:

        form = CustomerForm(
            instance=customer
        )

    return render(
        request,
        "customer_update.html",
        {
            "form": form,
            "customer": customer
        }
    )


# =========================================================
# ORDER STATUS UPDATE
# =========================================================

class OrderStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        request=OrderStatusUpdateSerializer,
        responses={
            200: dict,
            400: dict,
        },
        description="Updates the status of an order."
    )
    def patch(self, request, pk):

        order = get_object_or_404(
            Order,
            pk=pk
        )

        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context = {
                "order": order
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Order status updated successfully.",
                "order_number": order.order_number,
                "status": order.status,
            },
            status=status.HTTP_200_OK
        )

# =========================================================
# CUSTOMER REST API
# =========================================================

class CustomerViewSet(viewsets.ModelViewSet):

    queryset = Customer.objects.all()

    serializer_class = CustomerSerializer

    permission_classes = [
        IsAdminOrStaffReadOnly
    ]

    search_fields = [
        "customer_name",
        "email",
        "phone",
    ]

    ordering_fields = [
        "customer_name",
        "customer_since",
        "created_at",
        "updated_at",
    ]

    filterset_fields = [
        "is_active",
    ]


# =========================================================
# ORDER LIST / CREATE API
# =========================================================

class OrderViewSet(viewsets.ModelViewSet):

    queryset = (
        Order.objects
        .select_related("customer")
        .prefetch_related("items__product")
        .all()
    )

    permission_classes = [
        IsAuthenticated
    ]

    search_fields = [
        "order_number",
        "customer__customer_name",
        "customer__email",
    ]

    ordering_fields = [
        "order_number",
        "created_at",
        "updated_at",
        "total_amount",
        "status",
        "payment_status",
    ]

    filterset_fields = [
        "status",
        "payment_status",
        "customer",
    ]

    def get_serializer_class(self):

        if self.action == "create":
            return OrderCreateSerializer

        return OrderSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            order = serializer.save()

        except Exception as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response_serializer = OrderSerializer(
            order
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


# =========================================================
# ORDER DETAIL API
# =========================================================

class OrderDetailView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, pk):

        order = get_object_or_404(
            Order.objects
            .select_related("customer")
            .prefetch_related("items__product"),
            pk=pk
        )

        serializer = OrderSerializer(
            order
        )

        return Response(
            serializer.data
        )



# =========================================================
# PAYMENT STATUS UPDATE
# =========================================================

class PaymentStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        request=PaymentStatusUpdateSerializer,
        responses={
            200: dict,
            400: dict,
        },
        description="Updates the payment status of an order."
    )
    def patch(self, request, pk):

        order = get_object_or_404(
            Order,
            pk=pk
        )

        serializer = PaymentStatusUpdateSerializer(
            data=request.data,
            context={
                "order": order
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        payment_status = serializer.validated_data[
            "payment_status"
        ]

        order.payment_status = payment_status

        order.save(
            update_fields=[
                "payment_status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Payment status updated successfully.",
                "order_number": order.order_number,
                "payment_status": order.payment_status,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# CANCEL ORDER
# =========================================================

class CancelOrderView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @transaction.atomic
    def post(self, request, pk):

        order = get_object_or_404(
            Order.objects
            .prefetch_related("items__product"),
            pk=pk
        )

        if order.status == "CANCELLED":

            return Response(
                {
                    "detail": "Order is already cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == "DELIVERED":

            return Response(
                {
                    "detail": (
                        "Delivered orders cannot be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.payment_status == "PAID":
            return Response(
                {
                    "detail": (
                        "Paid orders cannot be cancelled. "
                        "Refund the payment first."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in order.items.all():

            product = item.product

            previous_quantity = product.quantity

            product.quantity += item.quantity

            product.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

            from Inventary.models import InventoryTransaction

            InventoryTransaction.objects.create(
                product=product,
                transaction_type="RETURN",
                quantity=item.quantity,
                previous_quantity=previous_quantity,
                new_quantity=product.quantity,
                reference=order.order_number,
                notes="Stock restored after order cancellation.",
            )

        order.status = "CANCELLED"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Order cancelled successfully.",
                "order_number": order.order_number,
                "status": order.status,
            }
        )

# =========================================================
# SALES REPORT
# =========================================================



class SalesReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Sales report",
        description=(
            "Returns overall sales statistics "
            "including total sales, today's sales, "
            "monthly sales and daily sales."
        ),
    )
    def get(self, request):

        orders = Order.objects.filter(
            payment_status="PAID"
        ).exclude(
            status="CANCELLED"
        )

        # -------------------------------------------------
        # TOTAL SALES
        # -------------------------------------------------

        total_sales = (
            orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # TODAY'S SALES
        # -------------------------------------------------

        today = timezone.localdate()

        today_sales = (
            orders.filter(
                order_date__date=today
            ).aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # THIS MONTH SALES
        # -------------------------------------------------

        current_month = today.month
        current_year = today.year

        this_month_sales = (
            orders.filter(
                order_date__year=current_year,
                order_date__month=current_month,
            ).aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # ORDER COUNT
        # -------------------------------------------------

        total_orders = orders.count()

        # -------------------------------------------------
        # DAILY SALES
        # -------------------------------------------------

        daily_sales = (
            orders
            .annotate(
                date=TruncDate("order_date")
            )
            .values("date")
            .annotate(
                sales=Sum("total_amount"),
                orders=Count("id"),
            )
            .order_by("-date")
        )

        # -------------------------------------------------
        # MONTHLY SALES
        # -------------------------------------------------

        monthly_sales = (
            orders
            .annotate(
                month=TruncMonth("order_date")
            )
            .values("month")
            .annotate(
                sales=Sum("total_amount"),
                orders=Count("id"),
            )
            .order_by("-month")
        )

        return Response(
            {
                "summary": {
                    "total_sales": total_sales,
                    "today_sales": today_sales,
                    "this_month_sales": this_month_sales,
                    "total_paid_orders": total_orders,
                },

                "daily_sales": list(
                    daily_sales
                ),

                "monthly_sales": list(
                    monthly_sales
                ),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# TOP SELLING PRODUCTS REPORT
# =========================================================

class TopSellingProductsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Top selling products report",
        description=(
            "Returns products ranked by quantity sold "
            "and revenue generated."
        ),
    )
    def get(self, request):

        top_products = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(
                total_quantity=Sum("quantity"),
                total_revenue=Sum("subtotal"),
                order_count=Count(
                    "order",
                    distinct=True
                ),
            )
            .order_by(
                "-total_quantity",
                "-total_revenue"
            )
        )

        return Response(
            {
                "count": top_products.count(),
                "results": list(top_products),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# CUSTOMER REVENUE REPORT
# =========================================================

class CustomerRevenueReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Customer revenue report",
        description=(
            "Returns customer-wise sales statistics "
            "including total orders, total quantity "
            "and total revenue."
        ),
    )
    def get(self, request):

        customer_revenue = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "order__customer",
                "order__customer__customer_name",
            )
            .annotate(
                total_orders=Count(
                    "order",
                    distinct=True
                ),
                total_quantity=Sum(
                    "quantity"
                ),
                total_revenue=Sum(
                    "subtotal"
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        return Response(
            {
                "count": customer_revenue.count(),
                "results": list(customer_revenue),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# CUSTOMER PERFORMANCE REPORT
# =========================================================

class CustomerPerformanceReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Customer performance report",
        description=(
            "Returns customer-wise performance including "
            "total orders, quantity purchased, revenue, "
            "average order value, cancelled orders, "
            "refunded orders and customer ranking."
        ),
    )
    def get(self, request):

        # =================================================
        # CUSTOMER SALES PERFORMANCE
        # =================================================

        customer_performance = (
            Customer.objects
            .annotate(

                total_orders=Count(
                    "orders",
                    filter=~models.Q(
                        orders__status="CANCELLED"
                    )
                    & ~models.Q(
                        orders__payment_status="REFUNDED"
                    ),
                    distinct=True
                ),

                total_quantity=Sum(
                    "orders__items__quantity",
                    filter=(
                        models.Q(
                            orders__payment_status="PAID"
                        )
                        & ~models.Q(
                            orders__status="CANCELLED"
                        )
                    )
                ),

                total_revenue=Sum(
                    "orders__items__subtotal",
                    filter=(
                        models.Q(
                            orders__payment_status="PAID"
                        )
                        & ~models.Q(
                            orders__status="CANCELLED"
                        )
                    )
                ),

                cancelled_orders=Count(
                    "orders",
                    filter=models.Q(
                        orders__status="CANCELLED"
                    ),
                    distinct=True
                ),

                refunded_orders=Count(
                    "orders",
                    filter=models.Q(
                        orders__payment_status="REFUNDED"
                    ),
                    distinct=True
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        results = []

        # =================================================
        # BUILD RESPONSE
        # =================================================

        for rank, customer in enumerate(
            customer_performance,
            start=1
        ):

            total_orders = (
                customer.total_orders
                or 0
            )

            total_quantity = (
                customer.total_quantity
                or 0
            )

            total_revenue = (
                customer.total_revenue
                or Decimal("0.00")
            )

            # ---------------------------------------------
            # AVERAGE ORDER VALUE
            # ---------------------------------------------

            if total_orders > 0:

                average_order_value = (
                    total_revenue
                    / Decimal(str(total_orders))
                )

            else:

                average_order_value = Decimal(
                    "0.00"
                )

            # ---------------------------------------------
            # RESULT
            # ---------------------------------------------

            results.append(
                {
                    "rank": rank,

                    "customer": customer.id,

                    "customer_name": (
                        customer.customer_name
                    ),

                    "email": customer.email,

                    "total_orders": total_orders,

                    "total_quantity": total_quantity,

                    "total_revenue": round(
                        total_revenue,
                        2
                    ),

                    "average_order_value": round(
                        average_order_value,
                        2
                    ),

                    "cancelled_orders": (
                        customer.cancelled_orders
                        or 0
                    ),

                    "refunded_orders": (
                        customer.refunded_orders
                        or 0
                    ),
                }
            )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# CATEGORY REVENUE REPORT
# =========================================================

class CategoryRevenueReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Category revenue report",
        description=(
            "Returns category-wise sales statistics "
            "including total orders, total quantity "
            "and total revenue."
        ),
    )
    def get(self, request):

        category_revenue = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "product__category",
                "product__category__name",
            )
            .annotate(
                total_orders=Count(
                    "order",
                    distinct=True
                ),
                total_quantity=Sum(
                    "quantity"
                ),
                total_revenue=Sum(
                    "subtotal"
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        return Response(
            {
                "count": category_revenue.count(),
                "results": list(category_revenue),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# PAYMENT SUMMARY REPORT
# =========================================================

class PaymentSummaryReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Payment summary report",
        description=(
            "Returns payment-wise statistics "
            "including order count and total amount."
        ),
    )
    def get(self, request):

        payment_summary = (
            Order.objects
            .values(
                "payment_status"
            )
            .annotate(
                total_orders=Count("id"),
                total_amount=Sum("total_amount"),
            )
            .order_by(
                "payment_status"
            )
        )

        return Response(
            {
                "count": payment_summary.count(),
                "results": list(payment_summary),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# ORDER STATUS SUMMARY REPORT
# =========================================================

class OrderStatusSummaryReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Order status summary report",
        description=(
            "Returns order-wise statistics grouped by "
            "order status, including total orders and "
            "total order amount."
        ),
    )
    def get(self, request):

        status_summary = (
            Order.objects
            .values(
                "status"
            )
            .annotate(
                total_orders=Count("id"),
                total_amount=Sum("total_amount"),
            )
            .order_by(
                "status"
            )
        )

        return Response(
            {
                "count": status_summary.count(),
                "results": list(status_summary),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# INVENTORY SALES PERFORMANCE REPORT
# =========================================================

class InventorySalesPerformanceView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Inventory sales performance report",
        description=(
            "Returns product-wise inventory and sales "
            "performance including current stock, "
            "quantity sold, revenue and order count."
        ),
    )
    def get(self, request):

        products = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "product",
                "product__product_name",
                "product__product_code",
                "product__quantity",
            )
            .annotate(
                total_quantity_sold=Sum(
                    "quantity"
                ),
                total_revenue=Sum(
                    "subtotal"
                ),
                total_orders=Count(
                    "order",
                    distinct=True
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        return Response(
            {
                "count": products.count(),
                "results": list(products),
            },
            status=status.HTTP_200_OK,
        )
# =========================================================
# LOW STOCK REPORT
# =========================================================

class LowStockReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Low stock report",
        description=(
            "Returns products that are low in stock "
            "or completely out of stock."
        ),
    )
    def get(self, request):

        from Inventary.models import Product

        products = (
            Product.objects
            .select_related("category", "supplier")
            .filter(
                quantity__lte=models.F("minimum_stock")
            )
            .order_by("quantity")
        )

        results = []

        for product in products:

            if product.is_out_of_stock:
                stock_status = "OUT_OF_STOCK"

            else:
                stock_status = "LOW_STOCK"

            results.append(
                {
                    "product": product.id,
                    "product_name": product.product_name,
                    "product_code": product.product_code,
                    "category": (
                        product.category.name
                        if product.category
                        else None
                    ),
                    "supplier": (
                        product.supplier.name
                        if product.supplier
                        else None
                    ),
                    "current_stock": product.quantity,
                    "minimum_stock": product.minimum_stock,
                    "maximum_stock": product.maximum_stock,
                    "unit": product.unit,
                    "status": stock_status,
                }
            )

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# DASHBOARD SUMMARY REPORT
# =========================================================

class DashboardSummaryView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Dashboard summary",
        description=(
            "Returns overall inventory, customer, order "
            "and sales statistics for the dashboard."
        ),
    )
    def get(self, request):

        from Inventary.models import Product

        # -------------------------------------------------
        # BASIC COUNTS
        # -------------------------------------------------

        total_products = Product.objects.filter(
            is_active=True
        ).count()

        total_customers = Customer.objects.filter(
            is_active=True
        ).count()

        total_orders = Order.objects.count()

        # -------------------------------------------------
        # ORDER STATUS COUNTS
        # -------------------------------------------------

        pending_orders = Order.objects.filter(
            status="PENDING"
        ).count()

        confirmed_orders = Order.objects.filter(
            status="CONFIRMED"
        ).count()

        processing_orders = Order.objects.filter(
            status="PROCESSING"
        ).count()

        shipped_orders = Order.objects.filter(
            status="SHIPPED"
        ).count()

        delivered_orders = Order.objects.filter(
            status="DELIVERED"
        ).count()

        cancelled_orders = Order.objects.filter(
            status="CANCELLED"
        ).count()

        # -------------------------------------------------
        # PAYMENT COUNTS
        # -------------------------------------------------

        paid_orders = Order.objects.filter(
            payment_status="PAID"
        ).count()

        pending_payments = Order.objects.filter(
            payment_status="PENDING"
        ).count()

        refunded_orders = Order.objects.filter(
            payment_status="REFUNDED"
        ).count()

        failed_payments = Order.objects.filter(
            payment_status="FAILED"
        ).count()

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        paid_orders_queryset = (
            Order.objects
            .filter(payment_status="PAID")
            .exclude(status="CANCELLED")
        )

        total_sales = (
            paid_orders_queryset.aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        today = timezone.localdate()

        today_sales = (
            paid_orders_queryset
            .filter(
                order_date__date=today
            )
            .aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # INVENTORY
        # -------------------------------------------------

        low_stock_products = Product.objects.filter(
            quantity__gt=0,
            quantity__lte=models.F("minimum_stock"),
            is_active=True
        ).count()

        out_of_stock_products = Product.objects.filter(
            quantity=0,
            is_active=True
        ).count()

        total_inventory_value = (
                Product.objects
                .filter(is_active=True)
                .aggregate(
                    total=Sum(
                        ExpressionWrapper(
                            F("quantity") * F("cost_price"),
                            output_field=DecimalField(
                                max_digits=18,
                                decimal_places=2,
                            ),
                        )
                    )
                )["total"]
                or Decimal("0.00")
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return Response(
            {
                "products": {
                    "total_products": total_products,
                    "low_stock_products": low_stock_products,
                    "out_of_stock_products": out_of_stock_products,
                },

                "customers": {
                    "total_customers": total_customers,
                },

                "orders": {
                    "total_orders": total_orders,
                    "pending": pending_orders,
                    "confirmed": confirmed_orders,
                    "processing": processing_orders,
                    "shipped": shipped_orders,
                    "delivered": delivered_orders,
                    "cancelled": cancelled_orders,
                },

                "payments": {
                    "paid_orders": paid_orders,
                    "pending_payments": pending_payments,
                    "failed_payments": failed_payments,
                    "refunded_orders": refunded_orders,
                },

                "sales": {
                    "total_sales": total_sales,
                    "today_sales": today_sales,
                },

                "inventory": {
                    "total_inventory_value": total_inventory_value,
                },
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# DATE RANGE SALES REPORT
# =========================================================

class DateRangeSalesReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Date range sales report",
        description=(
                "Returns sales statistics for a selected "
                "date range."
        ),
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Start date in YYYY-MM-DD format.",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in YYYY-MM-DD format.",
                required=True,
                type=str,
            ),
        ],
    )
    def get(self, request):

        start_date = request.query_params.get(
            "start_date"
        )

        end_date = request.query_params.get(
            "end_date"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not start_date or not end_date:

            return Response(
                {
                    "detail": (
                        "start_date and end_date are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            from datetime import datetime

            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            return Response(
                {
                    "detail": (
                        "Date format must be YYYY-MM-DD."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start > end:

            return Response(
                {
                    "detail": (
                        "start_date cannot be greater "
                        "than end_date."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # SALES QUERY
        # -------------------------------------------------

        orders = (
            Order.objects
            .filter(
                payment_status="PAID",
                order_date__date__gte=start,
                order_date__date__lte=end,
            )
            .exclude(
                status="CANCELLED"
            )
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        total_orders = orders.count()

        total_sales = (
            orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # DAILY SALES
        # -------------------------------------------------

        daily_sales = (
            orders
            .annotate(
                date=TruncDate("order_date")
            )
            .values("date")
            .annotate(
                sales=Sum("total_amount"),
                orders=Count("id"),
            )
            .order_by("-date")
        )

        # -------------------------------------------------
        # TOP PRODUCTS
        # -------------------------------------------------

        top_products = (
            OrderItem.objects
            .filter(
                order__in=orders
            )
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(
                total_quantity=Sum("quantity"),
                total_revenue=Sum("subtotal"),
            )
            .order_by(
                "-total_quantity",
                "-total_revenue"
            )[:10]
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return Response(
            {
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                },

                "summary": {
                    "total_orders": total_orders,
                    "total_sales": total_sales,
                },

                "daily_sales": list(
                    daily_sales
                ),

                "top_products": list(
                    top_products
                ),
            },

            status=status.HTTP_200_OK,
        )

# =========================================================
# PRODUCT PROFIT REPORT
# =========================================================

class ProductProfitReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Product profit report",
        description=(
            "Returns product-wise sales, cost, revenue "
            "and profit information for paid orders."
        ),
    )
    def get(self, request):

        profit_report = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(
                total_quantity=Sum(
                    "quantity"
                ),

                total_revenue=Sum(
                    "subtotal"
                ),

                total_cost=Sum(
                    ExpressionWrapper(
                        F("quantity") *
                        F("product__cost_price"),
                        output_field=DecimalField(
                            max_digits=12,
                            decimal_places=2,
                        ),
                    )
                ),

                total_orders=Count(
                    "order",
                    distinct=True
                ),
            )
            .annotate(
                total_profit=ExpressionWrapper(
                    F("total_revenue") -
                    F("total_cost"),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                )
            )
            .order_by(
                "-total_profit"
            )
        )

        return Response(
            {
                "count": profit_report.count(),
                "results": list(
                    profit_report
                ),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# SUPPLIER PERFORMANCE REPORT
# =========================================================

class SupplierPerformanceReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Supplier performance report",
        description=(
            "Returns supplier-wise inventory statistics "
            "including total products, current stock "
            "and inventory value."
        ),
    )
    def get(self, request):

        suppliers = (
            Supplier.objects
            .annotate(
                total_products=Count(
                    "products",
                    distinct=True
                ),

                active_products=Count(
                    "products",
                    filter=F(
                        "products__is_active"
                    ),
                    distinct=True
                ),

                total_stock=Sum(
                    "products__quantity"
                ),

                total_stock_value=Sum(
                    ExpressionWrapper(
                        F("products__quantity") *
                        F("products__cost_price"),
                        output_field=DecimalField(
                            max_digits=14,
                            decimal_places=2,
                        ),
                    )
                ),
            )
            .order_by(
                "-total_stock_value"
            )
        )

        results = []

        for supplier in suppliers:

            results.append(
                {
                    "supplier": supplier.id,
                    "supplier_name": supplier.name,
                    "company_name": supplier.company_name,
                    "total_products": (
                        supplier.total_products
                        or 0
                    ),
                    "active_products": (
                        supplier.active_products
                        or 0
                    ),
                    "total_stock": (
                        supplier.total_stock
                        or 0
                    ),
                    "total_stock_value": (
                        supplier.total_stock_value
                        or 0
                    ),
                }
            )

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# INVENTORY MOVEMENT REPORT
# =========================================================

class InventoryMovementReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Inventory movement report",
        description=(
            "Returns product-wise inventory movement "
            "including stock in, stock out, returns "
            "and total transactions."
        ),
    )
    def get(self, request):

        from django.db.models import Q, IntegerField
        from django.db.models import Case, When, Value

        movement = (
            InventoryTransaction.objects
            .select_related("product")
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(
                stock_in=Sum(
                    Case(
                        When(
                            transaction_type="IN",
                            then="quantity"
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),

                stock_out=Sum(
                    Case(
                        When(
                            transaction_type="OUT",
                            then="quantity"
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),

                returns=Sum(
                    Case(
                        When(
                            transaction_type="RETURN",
                            then="quantity"
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),

                adjustments=Sum(
                    Case(
                        When(
                            transaction_type="ADJUSTMENT",
                            then="quantity"
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),

                total_transactions=Count("id"),
            )
            .order_by(
                "-total_transactions"
            )
        )

        return Response(
            {
                "count": movement.count(),
                "results": list(movement),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# PRODUCT SALES DETAIL REPORT
# =========================================================

class ProductSalesDetailReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Product sales detail report",
        description=(
            "Returns detailed sales performance for each product "
            "including total orders, quantity sold, revenue "
            "and average selling price."
        ),
    )
    def get(self, request):

        product_sales = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(
                total_orders=Count(
                    "order",
                    distinct=True
                ),
                total_quantity=Sum(
                    "quantity"
                ),
                total_revenue=Sum(
                    "subtotal"
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        return Response(
            {
                "count": product_sales.count(),
                "results": list(product_sales),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# DAILY SALES TREND REPORT
# =========================================================

class DailySalesTrendView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Daily sales trend report",
        description=(
            "Returns daily sales performance "
            "including total orders, quantity sold "
            "and revenue."
        ),
    )
    def get(self, request):

        daily_sales = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .annotate(
                date=TruncDate("order__order_date")
            )
            .values("date")
            .annotate(
                total_orders=Count(
                    "order",
                    distinct=True
                ),
                total_quantity=Sum(
                    "quantity"
                ),
                total_revenue=Sum(
                    "subtotal"
                ),
            )
            .order_by("-date")
        )

        return Response(
            {
                "count": daily_sales.count(),
                "results": list(daily_sales),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# PRODUCT PERFORMANCE REPORT
# =========================================================

class ProductPerformanceReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Product performance report",
        description=(
            "Returns product-wise performance including "
            "orders, quantity sold, revenue, cost, profit, "
            "average selling price, profit margin and sales rank."
        ),
    )
    def get(self, request):

        product_performance = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(

                # -----------------------------------------
                # TOTAL ORDERS
                # -----------------------------------------

                total_orders=Count(
                    "order",
                    distinct=True
                ),

                # -----------------------------------------
                # TOTAL QUANTITY SOLD
                # -----------------------------------------

                total_quantity=Sum(
                    "quantity"
                ),

                # -----------------------------------------
                # TOTAL REVENUE
                # -----------------------------------------

                total_revenue=Sum(
                    "subtotal"
                ),

                # -----------------------------------------
                # TOTAL COST
                # -----------------------------------------

                total_cost=Sum(
                    ExpressionWrapper(
                        F("quantity")
                        * F("product__cost_price"),
                        output_field=DecimalField(
                            max_digits=14,
                            decimal_places=2
                        )
                    )
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        results = []

        # =================================================
        # CALCULATE PERFORMANCE
        # =================================================

        for rank, item in enumerate(
            product_performance,
            start=1
        ):

            total_revenue = (
                item["total_revenue"]
                or Decimal("0.00")
            )

            total_cost = (
                item["total_cost"]
                or Decimal("0.00")
            )

            total_quantity = (
                item["total_quantity"]
                or 0
            )

            # ---------------------------------------------
            # TOTAL PROFIT
            # ---------------------------------------------

            total_profit = (
                total_revenue
                - total_cost
            )

            # ---------------------------------------------
            # AVERAGE SELLING PRICE
            # ---------------------------------------------

            if total_quantity > 0:

                average_selling_price = (
                    total_revenue
                    / Decimal(str(total_quantity))
                )

            else:

                average_selling_price = Decimal("0.00")

            # ---------------------------------------------
            # PROFIT MARGIN
            # ---------------------------------------------

            if total_revenue > 0:

                profit_margin = (
                    total_profit
                    / total_revenue
                ) * Decimal("100")

            else:

                profit_margin = Decimal("0.00")

            # ---------------------------------------------
            # RESULT
            # ---------------------------------------------

            results.append(
                {
                    "rank": rank,

                    "product": item[
                        "product"
                    ],

                    "product_name": item[
                        "product__product_name"
                    ],

                    "product_code": item[
                        "product__product_code"
                    ],

                    "total_orders": item[
                        "total_orders"
                    ],

                    "total_quantity": total_quantity,

                    "total_revenue": round(
                        total_revenue,
                        2
                    ),

                    "total_cost": round(
                        total_cost,
                        2
                    ),

                    "average_selling_price": round(
                        average_selling_price,
                        2
                    ),

                    "total_profit": round(
                        total_profit,
                        2
                    ),

                    "profit_margin": round(
                        profit_margin,
                        2
                    ),
                }
            )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# FINANCIAL SUMMARY REPORT
# =========================================================

class FinancialSummaryReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Financial summary report",
        description=(
            "Returns overall financial statistics including "
            "revenue, cost, profit, profit margin, paid orders, "
            "refunded orders and net revenue."
        ),
    )
    def get(self, request):

        # =================================================
        # PAID ORDERS
        # =================================================

        paid_orders = (
            Order.objects
            .filter(
                payment_status="PAID"
            )
            .exclude(
                status="CANCELLED"
            )
        )

        # =================================================
        # REFUNDED ORDERS
        # =================================================

        refunded_orders = Order.objects.filter(
            payment_status="REFUNDED"
        )

        # =================================================
        # TOTAL REVENUE
        # =================================================

        total_revenue = (
            paid_orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # TOTAL COST
        # =================================================

        total_cost = (
            OrderItem.objects
            .filter(
                order__payment_status="PAID"
            )
            .exclude(
                order__status="CANCELLED"
            )
            .aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F("quantity")
                        * F("product__cost_price"),
                        output_field=DecimalField(
                            max_digits=14,
                            decimal_places=2
                        )
                    )
                )
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # GROSS PROFIT
        # =================================================

        gross_profit = (
            total_revenue
            - total_cost
        )

        # =================================================
        # PROFIT MARGIN
        # =================================================

        if total_revenue > 0:

            profit_margin = (
                gross_profit
                / total_revenue
            ) * Decimal("100")

        else:

            profit_margin = Decimal("0.00")

        # =================================================
        # REFUNDED AMOUNT
        # =================================================

        refunded_amount = (
            refunded_orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # NET REVENUE
        # =================================================

        net_revenue = (
            total_revenue
            - refunded_amount
        )

        # =================================================
        # ORDER COUNTS
        # =================================================

        paid_order_count = paid_orders.count()

        refunded_order_count = (
            refunded_orders.count()
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "revenue": {
                    "total_revenue": round(
                        total_revenue,
                        2
                    ),
                    "refunded_amount": round(
                        refunded_amount,
                        2
                    ),
                    "net_revenue": round(
                        net_revenue,
                        2
                    ),
                },

                "cost": {
                    "total_cost": round(
                        total_cost,
                        2
                    ),
                },

                "profit": {
                    "gross_profit": round(
                        gross_profit,
                        2
                    ),
                    "profit_margin": round(
                        profit_margin,
                        2
                    ),
                },

                "orders": {
                    "paid_orders": paid_order_count,
                    "refunded_orders": refunded_order_count,
                },
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# INVENTORY VALUATION REPORT
# =========================================================

class InventoryValuationReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Inventory valuation report",
        description=(
            "Returns inventory valuation including total "
            "quantity, cost value, selling value, potential "
            "profit, low-stock value and out-of-stock products."
        ),
    )
    def get(self, request):

        products = Product.objects.filter(
            is_active=True
        )

        # =================================================
        # TOTAL QUANTITY
        # =================================================

        total_quantity = (
            products.aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # =================================================
        # TOTAL COST VALUE
        # =================================================

        total_cost_value = (
            products.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("cost_price"),
                        output_field=DecimalField(
                            max_digits=18,
                            decimal_places=2
                        )
                    )
                )
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # TOTAL SELLING VALUE
        # =================================================

        total_selling_value = (
            products.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("selling_price"),
                        output_field=DecimalField(
                            max_digits=18,
                            decimal_places=2
                        )
                    )
                )
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # POTENTIAL PROFIT
        # =================================================

        potential_profit = (
            total_selling_value
            - total_cost_value
        )

        # =================================================
        # LOW STOCK
        # =================================================

        low_stock_products = products.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock")
        )

        low_stock_value = (
            low_stock_products.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("cost_price"),
                        output_field=DecimalField(
                            max_digits=18,
                            decimal_places=2
                        )
                    )
                )
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # OUT OF STOCK
        # =================================================

        out_of_stock_products = products.filter(
            quantity=0
        ).count()

        # =================================================
        # PRODUCT-WISE VALUATION
        # =================================================

        product_values = (
            products
            .annotate(
                cost_value=ExpressionWrapper(
                    F("quantity") * F("cost_price"),
                    output_field=DecimalField(
                        max_digits=18,
                        decimal_places=2
                    )
                ),

                selling_value=ExpressionWrapper(
                    F("quantity") * F("selling_price"),
                    output_field=DecimalField(
                        max_digits=18,
                        decimal_places=2
                    )
                ),
            )
            .order_by("-cost_value")
        )

        results = []

        for product in product_values:

            potential_product_profit = (
                product.selling_value
                - product.cost_value
            )

            if product.quantity == 0:

                stock_status = "OUT_OF_STOCK"

            elif product.quantity <= product.minimum_stock:

                stock_status = "LOW_STOCK"

            else:

                stock_status = "NORMAL"

            results.append(
                {
                    "product": product.id,
                    "product_name": product.product_name,
                    "product_code": product.product_code,

                    "quantity": product.quantity,

                    "unit": product.unit,

                    "cost_price": round(
                        product.cost_price,
                        2
                    ),

                    "selling_price": round(
                        product.selling_price,
                        2
                    ),

                    "cost_value": round(
                        product.cost_value,
                        2
                    ),

                    "selling_value": round(
                        product.selling_value,
                        2
                    ),

                    "potential_profit": round(
                        potential_product_profit,
                        2
                    ),

                    "stock_status": stock_status,
                }
            )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "summary": {
                    "total_products": products.count(),

                    "total_quantity": total_quantity,

                    "total_cost_value": round(
                        total_cost_value,
                        2
                    ),

                    "total_selling_value": round(
                        total_selling_value,
                        2
                    ),

                    "potential_profit": round(
                        potential_profit,
                        2
                    ),

                    "low_stock_products": (
                        low_stock_products.count()
                    ),

                    "low_stock_value": round(
                        low_stock_value,
                        2
                    ),

                    "out_of_stock_products": (
                        out_of_stock_products
                    ),
                },

                "products": results,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# ORDER ANALYTICS REPORT
# =========================================================

class OrderAnalyticsReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Order analytics report",
        description=(
            "Returns order analytics including total orders, "
            "paid orders, pending payments, refunded orders, "
            "average order value, cancellation rate, "
            "today's orders and monthly orders."
        ),
    )
    def get(self, request):

        # =================================================
        # ALL ORDERS
        # =================================================

        all_orders = Order.objects.all()

        # =================================================
        # BASIC COUNTS
        # =================================================

        total_orders = all_orders.count()

        paid_orders = all_orders.filter(
            payment_status="PAID"
        ).count()

        pending_payment_orders = all_orders.filter(
            payment_status="PENDING"
        ).count()

        refunded_orders = all_orders.filter(
            payment_status="REFUNDED"
        ).count()

        failed_payment_orders = all_orders.filter(
            payment_status="FAILED"
        ).count()

        cancelled_orders = all_orders.filter(
            status="CANCELLED"
        ).count()

        delivered_orders = all_orders.filter(
            status="DELIVERED"
        ).count()

        # =================================================
        # SALES ORDERS
        # =================================================

        sales_orders = all_orders.filter(
            payment_status="PAID"
        ).exclude(
            status="CANCELLED"
        )

        # =================================================
        # TOTAL REVENUE
        # =================================================

        total_revenue = (
            sales_orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # AVERAGE ORDER VALUE
        # =================================================

        if sales_orders.exists():

            average_order_value = (
                total_revenue
                / Decimal(str(sales_orders.count()))
            )

        else:

            average_order_value = Decimal(
                "0.00"
            )

        # =================================================
        # TODAY
        # =================================================

        today = timezone.localdate()

        today_orders = all_orders.filter(
            order_date__date=today
        )

        today_order_count = today_orders.count()

        today_revenue = (
            today_orders
            .filter(
                payment_status="PAID"
            )
            .exclude(
                status="CANCELLED"
            )
            .aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # THIS MONTH
        # =================================================

        this_month_orders = all_orders.filter(
            order_date__year=today.year,
            order_date__month=today.month,
        )

        this_month_order_count = (
            this_month_orders.count()
        )

        this_month_revenue = (
            this_month_orders
            .filter(
                payment_status="PAID"
            )
            .exclude(
                status="CANCELLED"
            )
            .aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # CANCELLATION RATE
        # =================================================

        if total_orders > 0:

            cancellation_rate = (
                Decimal(str(cancelled_orders))
                / Decimal(str(total_orders))
            ) * Decimal("100")

        else:

            cancellation_rate = Decimal(
                "0.00"
            )

        # =================================================
        # STATUS BREAKDOWN
        # =================================================

        status_breakdown = (
            all_orders
            .values("status")
            .annotate(
                total_orders=Count("id")
            )
            .order_by("-total_orders")
        )

        # =================================================
        # PAYMENT BREAKDOWN
        # =================================================

        payment_breakdown = (
            all_orders
            .values("payment_status")
            .annotate(
                total_orders=Count("id"),
                total_amount=Sum("total_amount"),
            )
            .order_by("-total_orders")
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "summary": {

                    "total_orders": total_orders,

                    "paid_orders": paid_orders,

                    "pending_payment_orders": (
                        pending_payment_orders
                    ),

                    "refunded_orders": refunded_orders,

                    "failed_payment_orders": (
                        failed_payment_orders
                    ),

                    "delivered_orders": (
                        delivered_orders
                    ),

                    "cancelled_orders": (
                        cancelled_orders
                    ),

                    "total_revenue": round(
                        total_revenue,
                        2
                    ),

                    "average_order_value": round(
                        average_order_value,
                        2
                    ),

                    "cancellation_rate": round(
                        cancellation_rate,
                        2
                    ),
                },

                "today": {

                    "orders": today_order_count,

                    "revenue": round(
                        today_revenue,
                        2
                    ),
                },

                "this_month": {

                    "orders": this_month_order_count,

                    "revenue": round(
                        this_month_revenue,
                        2
                    ),
                },

                "status_breakdown": list(
                    status_breakdown
                ),

                "payment_breakdown": list(
                    payment_breakdown
                ),
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# SALES GROWTH REPORT
# =========================================================

class SalesGrowthReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Sales growth report",
        description=(
            "Returns current month and previous month "
            "sales comparison including sales growth, "
            "order growth and daily sales trend."
        ),
    )
    def get(self, request):

        today = timezone.localdate()

        # =================================================
        # CURRENT MONTH
        # =================================================

        current_month_orders = (
            Order.objects
            .filter(
                order_date__year=today.year,
                order_date__month=today.month,
                payment_status="PAID",
            )
            .exclude(
                status="CANCELLED"
            )
        )

        current_sales = (
            current_month_orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        current_order_count = (
            current_month_orders.count()
        )

        # =================================================
        # PREVIOUS MONTH
        # =================================================

        if today.month == 1:

            previous_month = 12
            previous_year = today.year - 1

        else:

            previous_month = today.month - 1
            previous_year = today.year

        previous_month_orders = (
            Order.objects
            .filter(
                order_date__year=previous_year,
                order_date__month=previous_month,
                payment_status="PAID",
            )
            .exclude(
                status="CANCELLED"
            )
        )

        previous_sales = (
            previous_month_orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        previous_order_count = (
            previous_month_orders.count()
        )

        # =================================================
        # SALES GROWTH
        # =================================================

        if previous_sales > 0:

            sales_growth = (
                (
                    current_sales
                    - previous_sales
                )
                / previous_sales
            ) * Decimal("100")

        else:

            sales_growth = Decimal("0.00")

        # =================================================
        # ORDER GROWTH
        # =================================================

        if previous_order_count > 0:

            order_growth = (
                (
                    Decimal(
                        str(current_order_count)
                    )
                    - Decimal(
                        str(previous_order_count)
                    )
                )
                / Decimal(
                    str(previous_order_count)
                )
            ) * Decimal("100")

        else:

            order_growth = Decimal("0.00")

        # =================================================
        # DAILY SALES TREND
        # =================================================

        daily_sales = (
            current_month_orders
            .annotate(
                date=TruncDate("order_date")
            )
            .values("date")
            .annotate(
                sales=Sum("total_amount"),
                orders=Count("id"),
            )
            .order_by("date")
        )

        # =================================================
        # MONTHLY SALES TREND
        # =================================================

        monthly_sales = (
            Order.objects
            .filter(
                payment_status="PAID"
            )
            .exclude(
                status="CANCELLED"
            )
            .annotate(
                month=TruncMonth("order_date")
            )
            .values("month")
            .annotate(
                sales=Sum("total_amount"),
                orders=Count("id"),
            )
            .order_by("-month")
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "current_month": {
                    "year": today.year,
                    "month": today.month,
                    "sales": round(
                        current_sales,
                        2
                    ),
                    "orders": current_order_count,
                },

                "previous_month": {
                    "year": previous_year,
                    "month": previous_month,
                    "sales": round(
                        previous_sales,
                        2
                    ),
                    "orders": previous_order_count,
                },

                "growth": {
                    "sales_growth_percentage": round(
                        sales_growth,
                        2
                    ),
                    "order_growth_percentage": round(
                        order_growth,
                        2
                    ),
                },

                "daily_sales": list(
                    daily_sales
                ),

                "monthly_sales": list(
                    monthly_sales
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# CUSTOMER ANALYTICS REPORT
# =========================================================

class CustomerAnalyticsReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Customer analytics report",
        description=(
            "Returns customer-wise analytics including "
            "orders, quantity purchased, revenue, average "
            "order value, first order, last order, paid orders "
            "and cancelled orders."
        ),
    )
    def get(self, request):

        # =================================================
        # CUSTOMER ORDER DATA
        # =================================================

        customer_data = (
            Order.objects
            .select_related("customer")
            .values(
                "customer",
                "customer__customer_name",
            )
            .annotate(
                total_orders=Count("id"),

                total_quantity=Sum(
                    "items__quantity"
                ),

                total_revenue=Sum(
                    "total_amount",
                    filter=models.Q(
                        payment_status="PAID"
                    ),
                ),

                paid_orders=Count(
                    "id",
                    filter=models.Q(
                        payment_status="PAID"
                    ),
                ),

                cancelled_orders=Count(
                    "id",
                    filter=models.Q(
                        status="CANCELLED"
                    ),
                ),

                first_order_date=models.Min(
                    "order_date"
                ),

                last_order_date=models.Max(
                    "order_date"
                ),
            )
            .order_by(
                "-total_revenue"
            )
        )

        results = []

        # =================================================
        # BUILD RESPONSE
        # =================================================

        for rank, item in enumerate(
            customer_data,
            start=1
        ):

            total_revenue = (
                item["total_revenue"]
                or Decimal("0.00")
            )

            paid_orders = (
                item["paid_orders"]
                or 0
            )

            total_quantity = (
                item["total_quantity"]
                or 0
            )

            # ---------------------------------------------
            # AVERAGE ORDER VALUE
            # ---------------------------------------------

            if paid_orders > 0:

                average_order_value = (
                    total_revenue
                    / Decimal(
                        str(paid_orders)
                    )
                )

            else:

                average_order_value = Decimal(
                    "0.00"
                )

            results.append(
                {
                    "rank": rank,

                    "customer": item[
                        "customer"
                    ],

                    "customer_name": item[
                        "customer__customer_name"
                    ],

                    "total_orders": item[
                        "total_orders"
                    ],

                    "paid_orders": paid_orders,

                    "cancelled_orders": item[
                        "cancelled_orders"
                    ],

                    "total_quantity": total_quantity,

                    "total_revenue": round(
                        total_revenue,
                        2
                    ),

                    "average_order_value": round(
                        average_order_value,
                        2
                    ),

                    "first_order_date": (
                        item[
                            "first_order_date"
                        ]
                    ),

                    "last_order_date": (
                        item[
                            "last_order_date"
                        ]
                    ),
                }
            )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# INVENTORY HEALTH REPORT
# =========================================================

class InventoryHealthReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Inventory health report",
        description=(
            "Returns overall inventory health including "
            "stock levels, inventory value, low stock, "
            "out of stock and overstocked products."
        ),
    )
    def get(self, request):

        products = Product.objects.filter(
            is_active=True
        )

        # =================================================
        # BASIC COUNTS
        # =================================================

        total_products = products.count()

        out_of_stock_products = products.filter(
            quantity=0
        ).count()

        low_stock_products = products.filter(
            quantity__gt=0,
            quantity__lte=models.F("minimum_stock")
        ).count()

        healthy_stock_products = products.filter(
            quantity__gt=models.F("minimum_stock"),
            quantity__lte=models.F("maximum_stock")
        ).count()

        overstocked_products = products.filter(
            quantity__gt=models.F("maximum_stock")
        ).count()

        # =================================================
        # TOTAL STOCK QUANTITY
        # =================================================

        total_stock_quantity = (
            products.aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # =================================================
        # TOTAL INVENTORY VALUE
        # =================================================

        total_inventory_value = (
            products.aggregate(
                total=Sum(
                    models.F("quantity")
                    * models.F("cost_price")
                )
            )["total"]
            or Decimal("0.00")
        )

        # =================================================
        # AVERAGE STOCK VALUE
        # =================================================

        if total_products > 0:

            average_stock_value = (
                total_inventory_value
                / Decimal(
                    str(total_products)
                )
            )

        else:

            average_stock_value = Decimal(
                "0.00"
            )

        # =================================================
        # STOCK HEALTH %
        # =================================================

        if total_products > 0:

            stock_health_percentage = (
                Decimal(
                    str(healthy_stock_products)
                )
                / Decimal(
                    str(total_products)
                )
            ) * Decimal("100")

        else:

            stock_health_percentage = Decimal(
                "0.00"
            )

        # =================================================
        # LOW STOCK PRODUCTS
        # =================================================

        low_stock_list = (
            products
            .filter(
                quantity__lte=models.F(
                    "minimum_stock"
                )
            )
            .values(
                "id",
                "product_name",
                "product_code",
                "quantity",
                "minimum_stock",
                "maximum_stock",
            )
            .order_by("quantity")
        )

        # =================================================
        # OVERSTOCKED PRODUCTS
        # =================================================

        overstocked_list = (
            products
            .filter(
                quantity__gt=models.F(
                    "maximum_stock"
                )
            )
            .values(
                "id",
                "product_name",
                "product_code",
                "quantity",
                "minimum_stock",
                "maximum_stock",
            )
            .order_by("-quantity")
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "summary": {

                    "total_products": total_products,

                    "total_stock_quantity": (
                        total_stock_quantity
                    ),

                    "out_of_stock_products": (
                        out_of_stock_products
                    ),

                    "low_stock_products": (
                        low_stock_products
                    ),

                    "healthy_stock_products": (
                        healthy_stock_products
                    ),

                    "overstocked_products": (
                        overstocked_products
                    ),

                    "total_inventory_value": round(
                        total_inventory_value,
                        2
                    ),

                    "average_stock_value": round(
                        average_stock_value,
                        2
                    ),

                    "stock_health_percentage": round(
                        stock_health_percentage,
                        2
                    ),
                },

                "low_stock_products": list(
                    low_stock_list
                ),

                "overstocked_products": list(
                    overstocked_list
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# INVENTORY ACTIVITY / AUDIT REPORT
# =========================================================

class InventoryActivityReportView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Inventory activity report",
        description=(
            "Returns inventory transaction statistics "
            "including stock in, stock out, returns, "
            "adjustments and recent inventory activity."
        ),
    )
    def get(self, request):

        transactions = InventoryTransaction.objects.all()

        # =================================================
        # TRANSACTION COUNTS
        # =================================================

        total_transactions = transactions.count()

        stock_in_count = transactions.filter(
            transaction_type="IN"
        ).count()

        stock_out_count = transactions.filter(
            transaction_type="OUT"
        ).count()

        return_count = transactions.filter(
            transaction_type="RETURN"
        ).count()

        adjustment_count = transactions.filter(
            transaction_type="ADJUSTMENT"
        ).count()

        # =================================================
        # QUANTITY MOVEMENT
        # =================================================

        total_quantity_moved = (
            transactions.aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        total_stock_in_quantity = (
            transactions
            .filter(
                transaction_type="IN"
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        total_stock_out_quantity = (
            transactions
            .filter(
                transaction_type="OUT"
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        total_return_quantity = (
            transactions
            .filter(
                transaction_type="RETURN"
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        total_adjustment_quantity = (
            transactions
            .filter(
                transaction_type="ADJUSTMENT"
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # =================================================
        # PRODUCT-WISE MOVEMENT
        # =================================================

        product_movement = (
            transactions
            .values(
                "product",
                "product__product_name",
                "product__product_code",
            )
            .annotate(
                total_transactions=Count("id"),

                total_quantity=Sum(
                    "quantity"
                ),

                stock_in=Sum(
                    "quantity",
                    filter=models.Q(
                        transaction_type="IN"
                    ),
                ),

                stock_out=Sum(
                    "quantity",
                    filter=models.Q(
                        transaction_type="OUT"
                    ),
                ),

                returns=Sum(
                    "quantity",
                    filter=models.Q(
                        transaction_type="RETURN"
                    ),
                ),

                adjustments=Sum(
                    "quantity",
                    filter=models.Q(
                        transaction_type="ADJUSTMENT"
                    ),
                ),
            )
            .order_by(
                "-total_quantity"
            )
        )

        # =================================================
        # RECENT ACTIVITY
        # =================================================

        recent_activity = (
            transactions
            .select_related("product")
            .values(
                "id",
                "product",
                "product__product_name",
                "product__product_code",
                "transaction_type",
                "quantity",
                "previous_quantity",
                "new_quantity",
                "reference",
                "notes",
                "created_at",
            )
            .order_by(
                "-created_at"
            )[:20]
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "summary": {

                    "total_transactions": (
                        total_transactions
                    ),

                    "stock_in_count": (
                        stock_in_count
                    ),

                    "stock_out_count": (
                        stock_out_count
                    ),

                    "return_count": (
                        return_count
                    ),

                    "adjustment_count": (
                        adjustment_count
                    ),

                    "total_quantity_moved": (
                        total_quantity_moved
                    ),

                    "total_stock_in_quantity": (
                        total_stock_in_quantity
                    ),

                    "total_stock_out_quantity": (
                        total_stock_out_quantity
                    ),

                    "total_return_quantity": (
                        total_return_quantity
                    ),

                    "total_adjustment_quantity": (
                        total_adjustment_quantity
                    ),
                },

                "product_movement": list(
                    product_movement
                ),

                "recent_activity": list(
                    recent_activity
                ),
            },
            status=status.HTTP_200_OK,
        )