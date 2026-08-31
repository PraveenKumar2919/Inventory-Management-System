from django.db import transaction
from django.db.models import (
    F,
    Sum,
    DecimalField,
    ExpressionWrapper,
    Count,
    Avg,
)
from rest_framework import (
    status,
    viewsets,
    filters,
)
from django.utils import timezone
from datetime import timedelta
from .permissions import IsStaffOrAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from .models import (
    Category,
    Supplier,
    Product,
    InventoryTransaction,
)
from Ordermanagement.models import Customer, Order

from .serializers import (
    CategorySerializer,
    SupplierSerializer,
    ProductSerializer,
    InventoryTransactionSerializer,
    StockSerializer,
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
            "Returns sales analytics for today, week, "
            "month, year or all time."
        ),
    )
    def get(self, request):

        period = request.query_params.get(
            "period",
            "all"
        ).lower()

        today = timezone.localdate()

        # -------------------------------------------------
        # BASE ORDERS
        # -------------------------------------------------

        orders = (
            Order.objects
            .exclude(status="CANCELLED")
        )

        # -------------------------------------------------
        # DATE FILTER
        # -------------------------------------------------

        if period == "today":

            orders = orders.filter(
                order_date__date=today
            )

        elif period == "week":

            start_date = today - timedelta(
                days=6
            )

            orders = orders.filter(
                order_date__date__gte=start_date,
                order_date__date__lte=today,
            )

        elif period == "month":

            orders = orders.filter(
                order_date__year=today.year,
                order_date__month=today.month,
            )

        elif period == "year":

            orders = orders.filter(
                order_date__year=today.year
            )

        elif period != "all":

            return Response(
                {
                    "detail": (
                        "Invalid period. "
                        "Allowed values: "
                        "today, week, month, year, all"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # SALES CALCULATIONS
        # -------------------------------------------------

        summary = orders.aggregate(
            total_sales=Sum("total_amount"),
            total_tax=Sum("tax_amount"),
            total_discount=Sum("discount_amount"),
            average_order_value=Avg("total_amount"),
        )

        total_orders = orders.count()

        # -------------------------------------------------
        # ORDER STATUS COUNTS
        # -------------------------------------------------

        delivered_orders = orders.filter(
            status="DELIVERED"
        ).count()

        pending_orders = orders.filter(
            status="PENDING"
        ).count()

        confirmed_orders = orders.filter(
            status="CONFIRMED"
        ).count()

        processing_orders = orders.filter(
            status="PROCESSING"
        ).count()

        shipped_orders = orders.filter(
            status="SHIPPED"
        ).count()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return Response(
            {
                "period": period,

                "summary": {
                    "total_orders": total_orders,

                    "delivered_orders": (
                        delivered_orders
                    ),

                    "pending_orders": (
                        pending_orders
                    ),

                    "confirmed_orders": (
                        confirmed_orders
                    ),

                    "processing_orders": (
                        processing_orders
                    ),

                    "shipped_orders": (
                        shipped_orders
                    ),

                    "total_sales": (
                        summary["total_sales"]
                        or 0
                    ),

                    "total_tax": (
                        summary["total_tax"]
                        or 0
                    ),

                    "total_discount": (
                        summary["total_discount"]
                        or 0
                    ),

                    "average_order_value": (
                        summary[
                            "average_order_value"
                        ]
                        or 0
                    ),
                }
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# CATEGORY
# =========================================================

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = (
        Category.objects
        .all()
        .order_by("name")
    )

    serializer_class = CategorySerializer

    permission_classes = [
        IsStaffOrAdminOrReadOnly
    ]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "is_active",
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "name"
    ]


# =========================================================
# SUPPLIER
# =========================================================

class SupplierViewSet(viewsets.ModelViewSet):

    queryset = (
        Supplier.objects
        .all()
        .order_by("name")
    )

    serializer_class = SupplierSerializer

    permission_classes = [
        IsStaffOrAdminOrReadOnly
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "is_active",
    ]

    search_fields = [
        "name",
        "company_name",
        "email",
        "phone",
        "address",
    ]

    ordering_fields = [
        "name",
        "company_name",
        "email",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "name"
    ]


# =========================================================
# PRODUCT
# =========================================================

class ProductViewSet(viewsets.ModelViewSet):

    queryset = (
        Product.objects
        .select_related(
            "category",
            "supplier",
        )
        .all()
    )

    serializer_class = ProductSerializer

    permission_classes = [
        IsStaffOrAdminOrReadOnly
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    filterset_fields = {
        "category": ["exact"],
        "supplier": ["exact"],
        "food_product": ["exact"],
        "is_active": ["exact"],
    }

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search_fields = [
        "product_name",
        "product_code",
        "description",
        "category__name",
        "supplier__name",
    ]

    # -----------------------------------------------------
    # ORDERING
    # -----------------------------------------------------

    ordering_fields = [
        "product_name",
        "product_code",
        "cost_price",
        "selling_price",
        "quantity",
        "minimum_stock",
        "maximum_stock",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at"
    ]

    # =====================================================
    # LOW STOCK
    # =====================================================

    @extend_schema(
        summary="Get low-stock products",
        description=(
            "Returns active products whose quantity "
            "is below or equal to the minimum stock level."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="low-stock",
    )
    def low_stock(self, request):

        queryset = (
            self.get_queryset()
            .filter(
                is_active=True,
                quantity__lte=F("minimum_stock"),
                quantity__gt=0,
            )
        )

        page = self.paginate_queryset(
            queryset
        )

        if page is not None:

            serializer = self.get_serializer(
                page,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # OUT OF STOCK
    # =====================================================

    @extend_schema(
        summary="Get out-of-stock products",
        description=(
            "Returns active products whose "
            "available quantity is zero."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="out-of-stock",
    )
    def out_of_stock(self, request):

        queryset = (
            self.get_queryset()
            .filter(
                is_active=True,
                quantity=0,
            )
        )

        page = self.paginate_queryset(
            queryset
        )

        if page is not None:

            serializer = self.get_serializer(
                page,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# TRANSACTION HISTORY
# =========================================================

class InventoryTransactionListView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Get inventory transaction history",
        description=(
            "Returns stock IN and OUT transaction history."
        ),
        parameters=[
            OpenApiParameter(
                name="transaction_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="IN or OUT",
            ),
            OpenApiParameter(
                name="product",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Product ID",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
    )
    def get(self, request):

        queryset = (
            InventoryTransaction.objects
            .select_related(
                "product",
                "product__category",
                "product__supplier",
            )
            .all()
            .order_by("-created_at")
        )

        # -------------------------------------------------
        # FILTER BY TRANSACTION TYPE
        # -------------------------------------------------

        transaction_type = request.query_params.get(
            "transaction_type"
        )

        if transaction_type:

            transaction_type = (
                transaction_type.upper()
            )

            if transaction_type not in [
                "IN",
                "OUT",
            ]:

                return Response(
                    {
                        "detail": (
                            "transaction_type must "
                            "be IN or OUT."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(
                transaction_type=transaction_type
            )

        # -------------------------------------------------
        # FILTER BY PRODUCT
        # -------------------------------------------------

        product_id = request.query_params.get(
            "product"
        )

        if product_id:

            try:
                product_id = int(product_id)

            except ValueError:

                return Response(
                    {
                        "detail": (
                            "product must be a valid "
                            "product ID."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(
                product_id=product_id
            )

        # -------------------------------------------------
        # PAGINATION
        # -------------------------------------------------

        page_size = 10

        try:

            page = int(
                request.query_params.get(
                    "page",
                    1,
                )
            )

        except ValueError:

            page = 1

        if page < 1:
            page = 1

        total_count = queryset.count()

        start = (
            page - 1
        ) * page_size

        end = start + page_size

        transactions = queryset[
            start:end
        ]

        serializer = InventoryTransactionSerializer(
            transactions,
            many=True,
        )

        return Response(
            {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# STOCK IN
# =========================================================

class StockInView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Add stock to a product",
        description=(
            "Increases product quantity and creates "
            "an inventory transaction."
        ),
        request=StockSerializer,
        responses={
            200: ProductSerializer,
            400: StockSerializer,
            404: None,
        },
    )
    @transaction.atomic
    def post(self, request):

        # -------------------------------------------------
        # VALIDATE REQUEST
        # -------------------------------------------------

        serializer = StockSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product_id = serializer.validated_data[
            "product_id"
        ]

        quantity = serializer.validated_data[
            "quantity"
        ]

        reference = serializer.validated_data.get(
            "reference",
            "",
        )

        notes = serializer.validated_data.get(
            "notes",
            "",
        )

        # -------------------------------------------------
        # LOCK PRODUCT
        # -------------------------------------------------

        try:

            product = (
                Product.objects
                .select_for_update()
                .select_related(
                    "category",
                    "supplier",
                )
                .get(
                    id=product_id
                )
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "detail": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -------------------------------------------------
        # ACTIVE PRODUCT CHECK
        # -------------------------------------------------

        if not product.is_active:

            return Response(
                {
                    "detail": (
                        "Cannot add stock to "
                        "an inactive product."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # PREVIOUS STOCK
        # -------------------------------------------------

        previous_quantity = (
            product.quantity
        )

        # -------------------------------------------------
        # UPDATE STOCK
        # -------------------------------------------------

        product.quantity = (
            product.quantity + quantity
        )

        # -------------------------------------------------
        # MAXIMUM STOCK CHECK
        # -------------------------------------------------

        if (
            product.maximum_stock
            and product.quantity
            > product.maximum_stock
        ):

            return Response(
                {
                    "detail": (
                        "Stock quantity cannot exceed "
                        f"maximum stock limit of "
                        f"{product.maximum_stock}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        # -------------------------------------------------
        # CREATE TRANSACTION
        # -------------------------------------------------

        InventoryTransaction.objects.create(
            product=product,
            transaction_type="IN",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=product.quantity,
            reference=reference,
            notes=notes,
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        product_serializer = ProductSerializer(
            product
        )

        return Response(
            {
                "message": (
                    "Stock added successfully."
                ),
                "transaction_type": "IN",
                "quantity_added": quantity,
                "previous_quantity": previous_quantity,
                "new_quantity": product.quantity,
                "product": product_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# STOCK OUT
# =========================================================

class StockOutView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Remove stock from a product",
        description=(
            "Decreases product quantity and creates "
            "an inventory transaction."
        ),
        request=StockSerializer,
    )
    @transaction.atomic
    def post(self, request):

        # -------------------------------------------------
        # VALIDATE REQUEST
        # -------------------------------------------------

        serializer = StockSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product_id = serializer.validated_data[
            "product_id"
        ]

        quantity = serializer.validated_data[
            "quantity"
        ]

        reference = serializer.validated_data.get(
            "reference",
            "",
        )

        notes = serializer.validated_data.get(
            "notes",
            "",
        )

        # -------------------------------------------------
        # LOCK PRODUCT
        # -------------------------------------------------

        try:

            product = (
                Product.objects
                .select_for_update()
                .select_related(
                    "category",
                    "supplier",
                )
                .get(
                    id=product_id
                )
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "detail": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -------------------------------------------------
        # ACTIVE PRODUCT CHECK
        # -------------------------------------------------

        if not product.is_active:

            return Response(
                {
                    "detail": (
                        "Cannot remove stock from "
                        "an inactive product."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # STOCK VALIDATION
        # -------------------------------------------------

        if quantity > product.quantity:

            return Response(
                {
                    "detail": (
                        "Insufficient stock.",
                        f"Available stock: "
                        f"{product.quantity}",
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # PREVIOUS STOCK
        # -------------------------------------------------

        previous_quantity = (
            product.quantity
        )

        # -------------------------------------------------
        # UPDATE STOCK
        # -------------------------------------------------

        product.quantity = (
            product.quantity - quantity
        )

        product.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        # -------------------------------------------------
        # CREATE TRANSACTION
        # -------------------------------------------------

        InventoryTransaction.objects.create(
            product=product,
            transaction_type="OUT",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=product.quantity,
            reference=reference,
            notes=notes,
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        product_serializer = ProductSerializer(
            product
        )

        return Response(
            {
                "message": (
                    "Stock removed successfully."
                ),
                "transaction_type": "OUT",
                "quantity_removed": quantity,
                "previous_quantity": previous_quantity,
                "new_quantity": product.quantity,
                "product": product_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# DASHBOARD
# =========================================================

class DashboardView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Inventory and sales dashboard",
        description=(
            "Returns inventory, product, supplier, customer, "
            "order and sales statistics."
        ),
    )
    def get(self, request):

        # =================================================
        # PRODUCTS
        # =================================================

        products = Product.objects.all()

        total_products = products.count()

        active_products = products.filter(
            is_active=True
        ).count()

        inactive_products = products.filter(
            is_active=False
        ).count()

        # =================================================
        # TOTAL STOCK
        # =================================================

        total_stock = (
            products.aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # =================================================
        # STOCK VALUE
        # =================================================

        stock_value_expression = ExpressionWrapper(
            F("quantity") * F("cost_price"),
            output_field=DecimalField(
                max_digits=18,
                decimal_places=2,
            ),
        )

        total_stock_value = (
            products.aggregate(
                total=Sum(
                    stock_value_expression
                )
            )["total"]
            or 0
        )

        # =================================================
        # LOW STOCK
        # =================================================

        low_stock_products = (
            products
            .filter(
                is_active=True,
                quantity__lte=F("minimum_stock"),
                quantity__gt=0,
            )
            .count()
        )

        # =================================================
        # OUT OF STOCK
        # =================================================

        out_of_stock_products = (
            products
            .filter(
                is_active=True,
                quantity=0,
            )
            .count()
        )

        # =================================================
        # CATEGORIES
        # =================================================

        total_categories = Category.objects.count()

        active_categories = (
            Category.objects
            .filter(is_active=True)
            .count()
        )

        # =================================================
        # SUPPLIERS
        # =================================================

        total_suppliers = Supplier.objects.count()

        active_suppliers = (
            Supplier.objects
            .filter(is_active=True)
            .count()
        )

        # =================================================
        # CUSTOMERS
        # =================================================

        # Import Customer here to avoid circular imports

        total_customers = Customer.objects.count()

        active_customers = (
            Customer.objects
            .filter(is_active=True)
            .count()
        )

        # =================================================
        # ORDERS
        # =================================================

        total_orders = Order.objects.count()

        pending_orders = (
            Order.objects
            .filter(status="PENDING")
            .count()
        )

        confirmed_orders = (
            Order.objects
            .filter(status="CONFIRMED")
            .count()
        )

        processing_orders = (
            Order.objects
            .filter(status="PROCESSING")
            .count()
        )

        shipped_orders = (
            Order.objects
            .filter(status="SHIPPED")
            .count()
        )

        delivered_orders = (
            Order.objects
            .filter(status="DELIVERED")
            .count()
        )

        cancelled_orders = (
            Order.objects
            .filter(status="CANCELLED")
            .count()
        )

        # =================================================
        # SALES
        # =================================================

        # Cancelled orders are NOT counted as sales.
        sales_orders = (
            Order.objects
            .exclude(status="CANCELLED")
        )

        total_sales = (
            sales_orders.aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # =================================================
        # TODAY'S SALES
        # =================================================

        today = timezone.localdate()

        today_sales = (
            sales_orders
            .filter(
                order_date__date=today
            )
            .aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # =================================================
        # THIS MONTH'S SALES
        # =================================================

        current_month = today.month
        current_year = today.year

        monthly_sales = (
            sales_orders
            .filter(
                order_date__year=current_year,
                order_date__month=current_month,
            )
            .aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "products": {
                    "total": total_products,
                    "active": active_products,
                    "inactive": inactive_products,
                    "low_stock": low_stock_products,
                    "out_of_stock": out_of_stock_products,
                },

                "inventory": {
                    "total_stock": total_stock,
                    "total_stock_value": total_stock_value,
                },

                "categories": {
                    "total": total_categories,
                    "active": active_categories,
                },

                "suppliers": {
                    "total": total_suppliers,
                    "active": active_suppliers,
                },

                "customers": {
                    "total": total_customers,
                    "active": active_customers,
                },

                "orders": {
                    "total": total_orders,
                    "pending": pending_orders,
                    "confirmed": confirmed_orders,
                    "processing": processing_orders,
                    "shipped": shipped_orders,
                    "delivered": delivered_orders,
                    "cancelled": cancelled_orders,
                },

                "sales": {
                    "total": total_sales,
                    "today": today_sales,
                    "this_month": monthly_sales,
                },
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# LOW STOCK - SEPARATE API
# =========================================================

class LowStockProductsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="List low-stock products",
    )
    def get(self, request):

        queryset = (
            Product.objects
            .select_related(
                "category",
                "supplier",
            )
            .filter(
                is_active=True,
                quantity__lte=F(
                    "minimum_stock"
                ),
                quantity__gt=0,
            )
            .order_by(
                "quantity"
            )
        )

        page_size = 10

        try:

            page = int(
                request.query_params.get(
                    "page",
                    1,
                )
            )

        except ValueError:

            page = 1

        if page < 1:
            page = 1

        total_count = queryset.count()

        start = (
            page - 1
        ) * page_size

        end = start + page_size

        products = queryset[
            start:end
        ]

        serializer = ProductSerializer(
            products,
            many=True,
        )

        return Response(
            {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (
                    (
                        total_count
                        + page_size
                        - 1
                    )
                    // page_size
                ),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# OUT OF STOCK - SEPARATE API
# =========================================================

class OutOfStockProductsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="List out-of-stock products",
    )
    def get(self, request):

        queryset = (
            Product.objects
            .select_related(
                "category",
                "supplier",
            )
            .filter(
                is_active=True,
                quantity=0,
            )
            .order_by(
                "product_name"
            )
        )

        page_size = 10

        try:

            page = int(
                request.query_params.get(
                    "page",
                    1,
                )
            )

        except ValueError:

            page = 1

        if page < 1:
            page = 1

        total_count = queryset.count()

        start = (
            page - 1
        ) * page_size

        end = start + page_size

        products = queryset[
            start:end
        ]

        serializer = ProductSerializer(
            products,
            many=True,
        )

        return Response(
            {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (
                    (
                        total_count
                        + page_size
                        - 1
                    )
                    // page_size
                ),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )