from rest_framework import serializers

from .models import (
    Category,
    Supplier,
    Product,
    InventoryTransaction,
)


# =========================================================
# CATEGORY SERIALIZER
# =========================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


# =========================================================
# SUPPLIER SERIALIZER
# =========================================================

class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = "__all__"


# =========================================================
# PRODUCT SERIALIZER
# =========================================================

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True
    )

    stock_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    is_low_stock = serializers.BooleanField(
        read_only=True
    )

    is_out_of_stock = serializers.BooleanField(
        read_only=True
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "product_name",
            "product_code",

            "category",
            "category_name",

            "supplier",
            "supplier_name",

            "description",

            "cost_price",
            "selling_price",
            "gst",

            "quantity",
            "minimum_stock",
            "maximum_stock",

            "unit",
            "expiry_date",

            "food_product",
            "is_active",

            "stock_value",
            "is_low_stock",
            "is_out_of_stock",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "stock_value",
            "is_low_stock",
            "is_out_of_stock",
        ]


# =========================================================
# INVENTORY TRANSACTION SERIALIZER
# =========================================================

class InventoryTransactionSerializer(
    serializers.ModelSerializer
):

    product_name = serializers.CharField(
        source="product.product_name",
        read_only=True
    )

    product_code = serializers.CharField(
        source="product.product_code",
        read_only=True
    )

    class Meta:

        model = InventoryTransaction

        fields = [
            "id",
            "product",
            "product_name",
            "product_code",
            "transaction_type",
            "quantity",
            "previous_quantity",
            "new_quantity",
            "reference",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "previous_quantity",
            "new_quantity",
            "created_at",
        ]


# =========================================================
# STOCK SERIALIZER
# =========================================================

class StockSerializer(serializers.Serializer):

    product_id = serializers.IntegerField(
        min_value=1
    )

    quantity = serializers.IntegerField(
        min_value=1
    )

    reference = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )