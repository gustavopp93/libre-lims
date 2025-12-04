from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.exams.forms import ExamForm, ExamUpdateForm
from apps.exams.models import Exam


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
        return context

    def form_valid(self, form):
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
        return context

    def form_valid(self, form):
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
