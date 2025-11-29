from django import forms

from apps.billing.models import Company


class CompanyForm(forms.ModelForm):
    """Form for creating and editing company information"""

    class Meta:
        model = Company
        fields = ["business_name", "document_number", "phone_number", "email", "legal_address"]
        widgets = {
            "business_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese razon social"}),
            "document_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese RUC (11 caracteres)",
                    "maxlength": "11",
                    "minlength": "11",
                }
            ),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese telefono"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Ingrese correo electronico"}),
            "legal_address": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Ingrese direccion legal", "rows": 3}
            ),
        }
