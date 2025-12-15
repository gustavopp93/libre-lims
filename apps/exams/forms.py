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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo category sea opcional
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Sin categoría"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo category sea opcional
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Sin categoría"


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
            "order": forms.HiddenInput(),
        }
        labels = {
            "component_exam": "Examen Componente",
            "order": "Orden",
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent_exam", None)
        super().__init__(*args, **kwargs)

        # Optimización: El queryset no se renderiza en HTML (TomSelect carga via API)
        # Solo necesitamos cargar lo mínimo para validación
        if self.data:
            # Si hay datos POST, cargar todos los IDs para validación (solo IDs, no todos los campos)
            self.fields["component_exam"].queryset = Exam.objects.only("id")
        elif self.instance and self.instance.pk and self.instance.component_exam_id:
            # Si hay una instancia guardada, solo cargar ese examen específico
            self.fields["component_exam"].queryset = Exam.objects.filter(pk=self.instance.component_exam_id)
        else:
            # Si no hay datos ni instancia, queryset vacío
            self.fields["component_exam"].queryset = Exam.objects.none()


class BaseExamComponentFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        # Cambiar el widget del campo DELETE a HiddenInput
        if "DELETE" in form.fields:
            form.fields["DELETE"].widget = forms.HiddenInput()

    def clean(self):
        """Validar que no haya referencias circulares en los componentes"""
        super().clean()

        if any(self.errors):
            return

        parent_exam = self.instance
        if not parent_exam or not parent_exam.pk:
            return

        # Obtener todos los componentes que se están agregando/manteniendo
        component_ids = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                component_exam = form.cleaned_data.get("component_exam")
                if component_exam:
                    component_ids.append(component_exam.id)

        # Verificar que el examen padre no esté en la lista de componentes
        if parent_exam.pk in component_ids:
            raise forms.ValidationError("Un examen no puede incluirse a sí mismo como componente.")

        # Verificar referencias circulares: si algún componente tiene al padre como componente
        # (esto previene A->B, B->A)
        for component_id in component_ids:
            component = Exam.objects.get(pk=component_id)
            # Obtener todos los componentes del componente
            sub_component_ids = list(component.component_items.values_list("component_exam_id", flat=True))
            if parent_exam.pk in sub_component_ids:
                raise forms.ValidationError(
                    f"Referencia circular detectada: {component.name} ya contiene a {parent_exam.name} como componente."
                )


ExamComponentFormSet = inlineformset_factory(
    Exam,
    ExamComponent,
    form=ExamComponentForm,
    formset=BaseExamComponentFormSet,
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
