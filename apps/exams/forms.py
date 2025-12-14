from django import forms
from django.forms import inlineformset_factory

from apps.exams.models import Exam, ExamCategory, ExamComponent


class ExamUpdateForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "category", "price", "has_components"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre del examen",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "has_components": forms.CheckboxInput(
                attrs={
                    "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500",
                    "x-model": "hasComponents",
                }
            ),
        }
        labels = {
            "name": "Nombre del Examen",
            "category": "Categoría",
            "price": "Precio",
            "has_components": "¿Este examen es un panel/perfil con componentes?",
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "category", "price", "has_components"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre del examen",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "has_components": forms.CheckboxInput(
                attrs={
                    "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500",
                    "x-model": "hasComponents",
                }
            ),
        }
        labels = {
            "name": "Nombre del Examen",
            "category": "Categoría",
            "price": "Precio",
            "has_components": "¿Este examen es un panel/perfil con componentes?",
        }


class ExamComponentForm(forms.ModelForm):
    class Meta:
        model = ExamComponent
        fields = ["component_exam", "order"]
        widgets = {
            "component_exam": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "0",
                }
            ),
        }
        labels = {
            "component_exam": "Examen Componente",
            "order": "Orden",
        }

    def __init__(self, *args, **kwargs):
        parent_exam = kwargs.pop("parent_exam", None)
        super().__init__(*args, **kwargs)
        # Excluir el examen padre de la lista de componentes disponibles
        if parent_exam:
            self.fields["component_exam"].queryset = Exam.objects.exclude(pk=parent_exam.pk).filter(
                has_components=False
            )
        else:
            self.fields["component_exam"].queryset = Exam.objects.filter(has_components=False)


ExamComponentFormSet = inlineformset_factory(
    Exam,
    ExamComponent,
    form=ExamComponentForm,
    fk_name="parent_exam",
    fields=["component_exam", "order"],
    extra=0,
    can_delete=True,
)


class ExamCategoryForm(forms.ModelForm):
    class Meta:
        model = ExamCategory
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre de la categoría",
                }
            ),
        }
        labels = {
            "name": "Nombre de la Categoría",
        }


class ExamCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = ExamCategory
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500",
                    "placeholder": "Nombre de la categoría",
                }
            ),
        }
        labels = {
            "name": "Nombre de la Categoría",
        }
