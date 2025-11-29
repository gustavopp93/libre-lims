from django import forms

from apps.exams.models import Exam


class ExamUpdateForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "price"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre del examen",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
        }
        labels = {
            "name": "Nombre del Examen",
            "price": "Precio",
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["code", "name", "price"]
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Código único del examen",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre del examen",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
        }
        labels = {
            "code": "Código del Examen",
            "name": "Nombre del Examen",
            "price": "Precio",
        }
