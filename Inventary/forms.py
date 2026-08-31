from django import forms
from .models import Product, Category, Supplier


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category

        fields = [
            "name",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter category name",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter category description",
                    "rows": 3,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier

        fields = [
            "name",
            "company_name",
            "email",
            "phone",
            "address",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter contact person name",
                }
            ),

            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter company name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "supplier@example.com",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter supplier address",
                    "rows": 3,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "product_name",
            "product_code",
            "category",
            "supplier",
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
        ]

        widgets = {
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product name",
                }
            ),

            "product_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: PROD-1001",
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "supplier": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter product description",
                }
            ),

            "cost_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),

            "selling_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),

            "gst": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                    "placeholder": "18",
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "0",
                }
            ),

            "minimum_stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "10",
                }
            ),

            "maximum_stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "100",
                }
            ),

            "unit": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "piece / kg / litre",
                }
            ),

            "expiry_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "food_product": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        cost_price = cleaned_data.get("cost_price")
        selling_price = cleaned_data.get("selling_price")
        minimum_stock = cleaned_data.get("minimum_stock")
        maximum_stock = cleaned_data.get("maximum_stock")

        if (
            cost_price is not None
            and selling_price is not None
            and selling_price < cost_price
        ):
            self.add_error(
                "selling_price",
                "Selling price cannot be lower than cost price."
            )

        if (
            minimum_stock is not None
            and maximum_stock is not None
            and minimum_stock > maximum_stock
        ):
            self.add_error(
                "minimum_stock",
                "Minimum stock cannot be greater than maximum stock."
            )

        return cleaned_data