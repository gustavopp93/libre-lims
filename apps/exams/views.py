from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.exams.forms import (
    ExamCategoryForm,
    ExamCategoryUpdateForm,
    ExamComponentFormSet,
    ExamForm,
    ExamUpdateForm,
)
from apps.exams.models import Exam, ExamCategory


class ExamsListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = "exams/exam_list.html"
    context_object_name = "exams"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por nombre
        name = self.request.GET.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = self.request.GET.get("name", "")
        context["breadcrumbs"] = [
            {"name": "Exámenes", "url": None},
        ]
        return context


class CreateExamView(LoginRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "exams/exam_create.html"
    success_url = reverse_lazy("exams_list")
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Exámenes", "url": reverse_lazy("exams_list")},
            {"name": "Crear Examen", "url": None},
        ]
        if self.request.POST:
            context["component_formset"] = ExamComponentFormSet(self.request.POST)
        else:
            context["component_formset"] = ExamComponentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        component_formset = context["component_formset"]

        with transaction.atomic():
            # Generar código automáticamente
            last_exam = Exam.objects.order_by("-code").first()
            if last_exam and last_exam.code and last_exam.code.startswith("EX"):
                try:
                    last_number = int(last_exam.code[2:])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1

            form.instance.code = f"EX{new_number:05d}"

            self.object = form.save()

            if component_formset.is_valid():
                component_formset.instance = self.object
                component_formset.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, "Examen creado exitosamente")
        return super().form_valid(form)


class UpdateExamView(LoginRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamUpdateForm
    template_name = "exams/exam_update.html"
    success_url = reverse_lazy("exams_list")
    login_url = reverse_lazy("login")
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Exámenes", "url": reverse_lazy("exams_list")},
            {"name": f"Editar: {self.object.name}", "url": None},
        ]
        if self.request.POST:
            context["component_formset"] = ExamComponentFormSet(self.request.POST, instance=self.object)
        else:
            context["component_formset"] = ExamComponentFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        component_formset = context["component_formset"]

        with transaction.atomic():
            self.object = form.save()

            if component_formset.is_valid():
                component_formset.instance = self.object
                component_formset.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, "Examen actualizado exitosamente")
        return super().form_valid(form)


def search_exams_api(request):
    """API endpoint para buscar exámenes por nombre"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "No autenticado"}, status=401)

    name = request.GET.get("name", "")

    if not name:
        return JsonResponse({"exams": []})

    exams = Exam.objects.filter(name__icontains=name)[:10]  # Limitar a 10 resultados

    exams_data = [
        {
            "id": exam.id,
            "name": exam.name,
        }
        for exam in exams
    ]

    return JsonResponse({"exams": exams_data})


# ==================== EXAM CATEGORIES ====================


class ExamCategoriesListView(LoginRequiredMixin, ListView):
    model = ExamCategory
    template_name = "exams/category_list.html"
    context_object_name = "categories"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por nombre
        name = self.request.GET.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = self.request.GET.get("name", "")
        context["breadcrumbs"] = [
            {"name": "Categorías de Exámenes", "url": None},
        ]
        return context


class CreateExamCategoryView(LoginRequiredMixin, CreateView):
    model = ExamCategory
    form_class = ExamCategoryForm
    template_name = "exams/category_create.html"
    success_url = reverse_lazy("exam_categories_list")
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Categorías de Exámenes", "url": reverse_lazy("exam_categories_list")},
            {"name": "Crear Categoría", "url": None},
        ]
        return context

    def form_valid(self, form):
        # Generar código automáticamente
        last_category = ExamCategory.objects.order_by("-code").first()
        if last_category and last_category.code.startswith("CA"):
            try:
                last_number = int(last_category.code[2:])
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1

        form.instance.code = f"CA{new_number:03d}"

        messages.success(self.request, "Categoría creada exitosamente")
        return super().form_valid(form)


class UpdateExamCategoryView(LoginRequiredMixin, UpdateView):
    model = ExamCategory
    form_class = ExamCategoryUpdateForm
    template_name = "exams/category_update.html"
    success_url = reverse_lazy("exam_categories_list")
    login_url = reverse_lazy("login")
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Categorías de Exámenes", "url": reverse_lazy("exam_categories_list")},
            {"name": f"Editar: {self.object.name}", "url": None},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada exitosamente")
        return super().form_valid(form)
