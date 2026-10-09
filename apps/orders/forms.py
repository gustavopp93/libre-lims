from django import forms

from apps.orders.models import PaymentMethod


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre del método de pago",
                }
            ),
        }
        labels = {
            "name": "Nombre",
        }
        error_messages = {
            "name": {
                "unique": "Ya existe un método de pago con este nombre (puede estar eliminado).",
            },
        }
