from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.company_name or self.name


class Product(models.Model):

    product_name = models.CharField(max_length=200)
    product_code = models.CharField(
        max_length=100,
        unique=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    description = models.TextField(blank=True, null=True)

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    gst = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    quantity = models.PositiveIntegerField(default=0)

    minimum_stock = models.PositiveIntegerField(default=10)

    maximum_stock = models.PositiveIntegerField(default=100)

    unit = models.CharField(
        max_length=30,
        default="piece"
    )

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    food_product = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product_code"]),
            models.Index(fields=["product_name"]),
            models.Index(fields=["quantity"]),
        ]

    def __str__(self):
        return f"{self.product_name} ({self.product_code})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    @property
    def stock_value(self):
        return self.quantity * self.cost_price


class InventoryTransaction(models.Model):

    TRANSACTION_TYPES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
        ("ADJUSTMENT", "Adjustment"),
        ("RETURN", "Return"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    quantity = models.PositiveIntegerField()

    previous_quantity = models.PositiveIntegerField()

    new_quantity = models.PositiveIntegerField()

    reference = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.product.product_name} - "
            f"{self.transaction_type} - "
            f"{self.quantity}"
        )