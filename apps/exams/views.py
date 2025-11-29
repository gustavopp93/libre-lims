import logging
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from openpyxl import load_workbook

from .forms import ExamForm, ExamUpdateForm
from .models import Exam

logger = logging.getLogger(__name__)


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


class BulkUploadExamsView(LoginRequiredMixin, View):
    """Vista para carga masiva de exámenes desde archivo Excel"""

    login_url = reverse_lazy("login")
    template_name = "exams/bulk_upload.html"

    def get(self, request):
        from django.shortcuts import render

        context = {
            "breadcrumbs": [
                {"name": "Exámenes", "url": reverse_lazy("exams_list")},
                {"name": "Carga Masiva", "url": None},
            ],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Validar que se haya enviado un archivo
        if "excel_file" not in request.FILES:
            messages.error(request, "No se ha seleccionado ningún archivo")
            return redirect("bulk_upload_exams")

        excel_file = request.FILES["excel_file"]

        # Validar que sea un archivo Excel
        if not excel_file.name.endswith((".xlsx", ".xls")):
            messages.error(request, "El archivo debe ser un archivo Excel (.xlsx o .xls)")
            return redirect("bulk_upload_exams")

        try:
            # Cargar el archivo Excel
            workbook = load_workbook(excel_file)
            sheet = workbook.active

            # Contadores
            updated_count = 0
            created_count = 0
            errors = []

            # Procesar las filas (empezando desde la fila 2, ya que la 1 es la cabecera)
            with transaction.atomic():
                for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    # Validar que la fila tenga al menos 3 columnas
                    if not row or len(row) < 3:
                        continue

                    code = row[0]
                    name = row[1]
                    price = row[2]

                    # Validar que code y name no estén vacíos
                    if not code or not name:
                        errors.append(f"Fila {row_num}: Código o nombre vacío")
                        continue

                    # Convertir code a string
                    code = str(code).strip()
                    name = str(name).strip()

                    # Validar y convertir el precio
                    try:
                        price_decimal = Decimal(str(price))
                        if price_decimal < 0:
                            errors.append(f"Fila {row_num}: El precio no puede ser negativo")
                            continue
                    except (InvalidOperation, ValueError, TypeError):
                        errors.append(f"Fila {row_num}: Precio inválido '{price}'")
                        continue

                    # Buscar si el examen existe por código
                    try:
                        exam = Exam.objects.get(code=code)
                        # Actualizar el precio
                        exam.price = price_decimal
                        exam.save()
                        updated_count += 1
                    except Exam.DoesNotExist:
                        # Crear nuevo examen
                        Exam.objects.create(code=code, name=name, price=price_decimal)
                        created_count += 1

            # Mostrar mensajes de resultado
            if created_count > 0:
                messages.success(request, f"Se crearon {created_count} exámenes")
            if updated_count > 0:
                messages.success(request, f"Se actualizaron {updated_count} exámenes")
            if errors:
                for error in errors[:10]:  # Mostrar solo los primeros 10 errores
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f"Y {len(errors) - 10} errores más...")

            if created_count == 0 and updated_count == 0:
                messages.warning(request, "No se procesó ningún examen")

            return redirect("exams_list")

        except Exception as e:
            logger.exception("Error al procesar el archivo de exámenes")
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            return redirect("bulk_upload_exams")
