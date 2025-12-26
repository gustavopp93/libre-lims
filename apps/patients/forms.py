from django import forms

from apps.patients.models import LeadSource, Patient


class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["phone_number", "email", "presumptive_diagnosis"]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Número de teléfono",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "correo@ejemplo.com",
                }
            ),
            "presumptive_diagnosis": forms.Textarea(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Ingrese la presunción médica del paciente",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "phone_number": "Teléfono",
            "email": "Correo Electrónico",
            "presumptive_diagnosis": "Presunción Médica",
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                "placeholder": "Ingrese su usuario",
                "required": True,
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                "placeholder": "Ingrese su contraseña",
                "required": True,
            }
        )
    )


class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar lead_source por name
        self.fields["lead_source"].queryset = LeadSource.objects.filter(is_active=True).order_by("name")

    class Meta:
        model = Patient
        fields = [
            "document_type",
            "document_number",
            "first_name",
            "last_name",
            "birthdate",
            "sex",
            "phone_number",
            "email",
            "lead_source",
            "presumptive_diagnosis",
        ]
        widgets = {
            "document_type": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                }
            ),
            "document_number": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Número de documento",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombres del paciente",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Apellidos del paciente",
                }
            ),
            "birthdate": forms.DateInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "type": "date",
                }
            ),
            "sex": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Número de teléfono",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "correo@ejemplo.com",
                }
            ),
            "lead_source": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                }
            ),
            "presumptive_diagnosis": forms.Textarea(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Ingrese la presunción médica del paciente",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "document_type": "Tipo de Documento",
            "document_number": "Número de Documento",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "birthdate": "Fecha de Nacimiento",
            "sex": "Sexo",
            "phone_number": "Teléfono",
            "email": "Correo Electrónico",
            "lead_source": "¿Cómo nos conoció?",
            "presumptive_diagnosis": "Presunción Médica",
        }


class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre del canal",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Descripción (opcional)",
                    "rows": 3,
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-5 w-5 text-blue-600",
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "is_active": "Activo",
        }
