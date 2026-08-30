from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Product, InventoryTransaction


@transaction.atomic
def stock_in(product_id, quantity, reference=None, notes=None):
    """
    Add stock to a product.
    """

    if quantity <= 0:
        raise ValidationError("Stock quantity must be greater than zero.")

    product = Product.objects.select_for_update().get(
        id=product_id
    )

    previous_quantity = product.quantity
    new_quantity = previous_quantity + quantity

    product.quantity = new_quantity
    product.save(update_fields=["quantity", "updated_at"])

    InventoryTransaction.objects.create(
        product=product,
        transaction_type="IN",
        quantity=quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reference=reference,
        notes=notes,
    )

    return product


@transaction.atomic
def stock_out(product_id, quantity, reference=None, notes=None):
    """
    Remove stock from a product.
    """

    if quantity <= 0:
        raise ValidationError("Stock quantity must be greater than zero.")

    product = Product.objects.select_for_update().get(
        id=product_id
    )

    previous_quantity = product.quantity

    if quantity > previous_quantity:
        raise ValidationError(
            f"Insufficient stock. Available stock: {previous_quantity}"
        )

    new_quantity = previous_quantity - quantity

    product.quantity = new_quantity
    product.save(update_fields=["quantity", "updated_at"])

    InventoryTransaction.objects.create(
        product=product,
        transaction_type="OUT",
        quantity=quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reference=reference,
        notes=notes,
    )

    return product


@transaction.atomic
def adjust_stock(product_id, new_quantity, reference=None, notes=None):
    """
    Adjust product stock to an exact quantity.
    """

    if new_quantity < 0:
        raise ValidationError(
            "Stock quantity cannot be negative."
        )

    product = Product.objects.select_for_update().get(
        id=product_id
    )

    previous_quantity = product.quantity

    if previous_quantity == new_quantity:
        raise ValidationError(
            "New quantity is the same as current quantity."
        )

    difference = abs(new_quantity - previous_quantity)

    product.quantity = new_quantity
    product.save(update_fields=["quantity", "updated_at"])

    InventoryTransaction.objects.create(
        product=product,
        transaction_type="ADJUSTMENT",
        quantity=difference,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reference=reference,
        notes=notes,
    )

    return product


@transaction.atomic
def return_stock(product_id, quantity, reference=None, notes=None):
    """
    Add returned stock back into inventory.
    """

    if quantity <= 0:
        raise ValidationError(
            "Return quantity must be greater than zero."
        )

    product = Product.objects.select_for_update().get(
        id=product_id
    )

    previous_quantity = product.quantity
    new_quantity = previous_quantity + quantity

    product.quantity = new_quantity
    product.save(update_fields=["quantity", "updated_at"])

    InventoryTransaction.objects.create(
        product=product,
        transaction_type="RETURN",
        quantity=quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reference=reference,
        notes=notes,
    )

    return product