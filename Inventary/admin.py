from django.contrib import admin
from .models import (
    Category,
    Supplier,
    Product,
    InventoryTransaction,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = ("name", "description")

    list_filter = ("is_active",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company_name",
        "email",
        "phone",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "company_name",
        "email",
        "phone",
    )

    list_filter = ("is_active",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "product_code",
        "product_name",
        "category",
        "supplier",
        "cost_price",
        "selling_price",
        "quantity",
        "minimum_stock",
        "stock_status",
        "food_product",
        "is_active",
    )

    search_fields = (
        "product_name",
        "product_code",
        "category__name",
        "supplier__name",
        "supplier__company_name",
    )

    list_filter = (
        "category",
        "supplier",
        "food_product",
        "is_active",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "stock_value",
        "stock_status",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "product_name",
                    "product_code",
                    "category",
                    "supplier",
                    "description",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "cost_price",
                    "selling_price",
                    "gst",
                )
            },
        ),
        (
            "Inventory",
            {
                "fields": (
                    "quantity",
                    "minimum_stock",
                    "maximum_stock",
                    "unit",
                    "stock_value",
                    "stock_status",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "expiry_date",
                    "food_product",
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def stock_status(self, obj):
        if obj.is_out_of_stock:
            return "OUT OF STOCK"

        if obj.is_low_stock:
            return "LOW STOCK"

        return "IN STOCK"

    stock_status.short_description = "Stock Status"


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "transaction_type",
        "quantity",
        "previous_quantity",
        "new_quantity",
        "reference",
        "created_at",
    )

    search_fields = (
        "product__product_name",
        "product__product_code",
        "reference",
        "notes",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("-created_at",)