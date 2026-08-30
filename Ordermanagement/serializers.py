
from decimal import Decimal

from django.db import transaction

from rest_framework import serializers

from .models import Customer, Order, OrderItem
from Inventary.models import Product, InventoryTransaction

# =========================================================
# CUSTOMER SERIALIZER
# =========================================================

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer

        fields = [
            "id",
            "customer_name",
            "customer_since",
            "email",
            "phone",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# =========================================================
# ORDER ITEM SERIALIZER
# =========================================================

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.product_name",
        read_only=True
    )

    product_code = serializers.CharField(
        source="product.product_code",
        read_only=True
    )

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "product_code",
            "quantity",
            "unit_price",
            "subtotal",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "product_code",
            "subtotal",
            "created_at",
            "updated_at",
        ]

    def validate_product(self, product):

        if not product.is_active:
            raise serializers.ValidationError(
                "This product is inactive."
            )

        return product

    def validate_quantity(self, quantity):

        if quantity <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity

    def validate(self, attrs):

        product = attrs.get("product")
        quantity = attrs.get("quantity")

        if product and quantity:

            if product.quantity < quantity:
                raise serializers.ValidationError({
                    "quantity": (
                        f"Insufficient stock. "
                        f"Available stock: {product.quantity}"
                    )
                })

        return attrs


# =========================================================
# ORDER LIST SERIALIZER
# =========================================================

class OrderListSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.customer_name",
        read_only=True
    )

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",
            "customer",
            "customer_name",
            "order_date",
            "status",
            "payment_status",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "item_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order_number",
            "order_date",
            "subtotal",
            "total_amount",
            "item_count",
            "created_at",
            "updated_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


# =========================================================
# ORDER DETAIL SERIALIZER
# =========================================================

class OrderDetailSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.customer_name",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",
            "customer",
            "customer_name",
            "order_date",
            "status",
            "payment_status",
            "shipping_address",
            "notes",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "item_count",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order_number",
            "order_date",
            "subtotal",
            "total_amount",
            "item_count",
            "items",
            "created_at",
            "updated_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


# =========================================================
# ORDER ITEM CREATE SERIALIZER
# =========================================================

class OrderItemCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem

        fields = [
            "product",
            "quantity",
        ]

    def validate_product(self, product):

        if not product.is_active:
            raise serializers.ValidationError(
                "This product is inactive."
            )

        return product

    def validate_quantity(self, quantity):

        if quantity <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity


# =========================================================
# ORDER CREATE SERIALIZER
# =========================================================

class OrderCreateSerializer(serializers.ModelSerializer):

    items = OrderItemCreateSerializer(
        many=True
    )

    class Meta:
        model = Order

        fields = [
            "customer",
            "shipping_address",
            "notes",
            "tax_amount",
            "discount_amount",
            "items",
        ]

    def validate_customer(self, customer):

        if not customer.is_active:
            raise serializers.ValidationError(
                "This customer is inactive."
            )

        return customer

    def validate_items(self, items):

        if not items:
            raise serializers.ValidationError(
                "Order must contain at least one item."
            )

        product_ids = [
            item["product"].id
            for item in items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "The same product cannot be added multiple times."
            )

        return items

    @transaction.atomic
    def create(self, validated_data):

        items_data = validated_data.pop("items")

        tax_amount = validated_data.get(
            "tax_amount",
            Decimal("0.00")
        )

        discount_amount = validated_data.get(
            "discount_amount",
            Decimal("0.00")
        )

        # -------------------------------------------------
        # Create Order
        # -------------------------------------------------

        order = Order.objects.create(
            **validated_data,
            subtotal=Decimal("0.00"),
            total_amount=Decimal("0.00"),
        )

        subtotal = Decimal("0.00")

        # -------------------------------------------------
        # Create Order Items
        # -------------------------------------------------

        for item_data in items_data:

            product = item_data["product"]
            quantity = item_data["quantity"]

            # Lock product row during transaction
            product = Product.objects.select_for_update().get(
                id=product.id
            )

            # Check stock again
            if product.quantity < quantity:

                raise serializers.ValidationError({
                    "stock": (
                        f"Insufficient stock for "
                        f"{product.product_name}. "
                        f"Available: {product.quantity}"
                    )
                })

            unit_price = product.selling_price

            item_subtotal = (
                unit_price * quantity
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=item_subtotal,
            )

            subtotal += item_subtotal

            # -------------------------------------------------
            # Reduce Inventory + Create Transaction
            # -------------------------------------------------

            previous_quantity = product.quantity

            product.quantity -= quantity

            product.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

            InventoryTransaction.objects.create(
                product=product,
                transaction_type="OUT",
                quantity=quantity,
                previous_quantity=previous_quantity,
                new_quantity=product.quantity,
                reference=order.order_number,
                notes=f"Stock issued for order {order.order_number}",
            )

        # -------------------------------------------------
        # Calculate Order Total
        # -------------------------------------------------

        total_amount = (
            subtotal
            + tax_amount
            - discount_amount
        )

        if total_amount < Decimal("0.00"):
            total_amount = Decimal("0.00")

        order.subtotal = subtotal
        order.total_amount = total_amount

        order.save(
            update_fields=[
                "subtotal",
                "total_amount",
                "updated_at",
            ]
        )

        return order


# =========================================================
# ORDER SERIALIZER
# =========================================================

class OrderSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.customer_name",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",
            "customer",
            "customer_name",
            "order_date",
            "status",
            "payment_status",
            "shipping_address",
            "notes",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "item_count",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order_number",
            "order_date",
            "subtotal",
            "total_amount",
            "item_count",
            "items",
            "created_at",
            "updated_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()

    # =========================================================
    # ORDER STATUS UPDATE SERIALIZER
    # =========================================================

class OrderStatusUpdateSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=Order.ORDER_STATUS_CHOICES
    )

    def validate_status(self, value):

        order = self.context.get("order")

        if not order:
            return value

        current_status = order.status

            # Payment must be completed before delivery
        if (
                value == "DELIVERED"
                and order.payment_status != "PAID"
        ):
            raise serializers.ValidationError(
                "Order cannot be delivered until payment is PAID."
            )

        allowed_transitions = {
            "PENDING": [
                "CONFIRMED",
                "CANCELLED",
            ],

            "CONFIRMED": [
                "PROCESSING",
                "CANCELLED",
            ],

            "PROCESSING": [
                "SHIPPED",
                "CANCELLED",
            ],

            "SHIPPED": [
                "DELIVERED",
            ],

            "DELIVERED": [],

            "CANCELLED": [],
        }

            # Same status
        if value == current_status:
            raise serializers.ValidationError(
                f"Order is already {current_status}."
            )

            # Invalid transition
        allowed = allowed_transitions.get(
            current_status,
            []
        )

        if value not in allowed:
            raise serializers.ValidationError(
                f"Invalid status transition: "
                f"{current_status} → {value}. "
                f"Allowed transitions: {allowed}"
            )

        return value
        # =========================================================
        # PAYMENT STATUS UPDATE SERIALIZER
        # =========================================================


class PaymentStatusUpdateSerializer(serializers.Serializer):
    payment_status = serializers.ChoiceField(
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("FAILED", "Failed"),
            ("REFUNDED", "Refunded"),
        ]
    )

    def validate_payment_status(self, value):

        order = self.context.get("order")

        if not order:
            return value

        current_status = order.payment_status

        allowed_transitions = {

            "PENDING": [
                "PAID",
                "FAILED",
            ],

            "FAILED": [
                "PENDING",
                "PAID",
            ],

            "PAID": [
                "REFUNDED",
            ],

            "REFUNDED": [],

        }

        if value == current_status:
            raise serializers.ValidationError(
                f"Payment is already {current_status}."
            )

        if value not in allowed_transitions.get(
                current_status,
                []
        ):
            raise serializers.ValidationError(
                f"Invalid payment transition: "
                f"{current_status} → {value}. "
                f"Allowed transitions: "
                f"{allowed_transitions.get(current_status, [])}"
            )

        return value