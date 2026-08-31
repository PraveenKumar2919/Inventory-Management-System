
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Customer(models.Model):

    customer_name = models.CharField(
        max_length=100
    )

    customer_since = models.DateField(
        null=True,
        blank=True
    )

    email = models.EmailField(
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.customer_name


class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=30,
        unique=True
    )

    order_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="PENDING"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    shipping_address = models.TextField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ]
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ]
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ]
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["order_number"]
            ),
            models.Index(
                fields=["status"]
            ),
            models.Index(
                fields=["payment_status"]
            ),
            models.Index(
                fields=["order_date"]
            ),
        ]

    def save(self, *args, **kwargs):

        if not self.order_number:

            # Find the highest numeric order number
            # instead of relying only on the latest ID.

            existing_numbers = []

            for order in (
                Order.objects
                .exclude(order_number="")
                .values_list(
                    "order_number",
                    flat=True
                )
            ):
                try:
                    number = int(
                        order.split("-")[-1]
                    )
                    existing_numbers.append(number)

                except (ValueError, IndexError):
                    continue

            if existing_numbers:
                next_number = (
                    max(existing_numbers) + 1
                )
            else:
                next_number = 1

            # Extra safety check against duplicate
            # order numbers.

            while Order.objects.filter(
                order_number=f"ORD-{next_number:06d}"
            ).exists():

                next_number += 1

            self.order_number = (
                f"ORD-{next_number:06d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.order_number} - "
            f"{self.customer.customer_name}"
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "Inventary.Product",
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ]
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["order"]
            ),
            models.Index(
                fields=["product"]
            ),
        ]

    def save(self, *args, **kwargs):

        self.subtotal = (
            Decimal(self.quantity)
            * self.unit_price
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.order.order_number} - "
            f"{self.product.product_name} - "
            f"{self.quantity}"
        )

