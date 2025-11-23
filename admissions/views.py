import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView
from weasyprint import HTML

from exams.models import Exam
from patients.models import Patient

from .models import Sale, SaleDetail


class SalesListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "admissions/sales_list.html"
    context_object_name = "sales"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Sale.objects.select_related("patient").prefetch_related("details__exam").order_by("-created_at")


class CreateTicketView(LoginRequiredMixin, TemplateView):
    template_name = "admissions/create_ticket.html"
    login_url = reverse_lazy("login")


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "admissions/sale_detail.html"
    context_object_name = "sale"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Sale.objects.select_related("patient").prefetch_related("details__exam")


class SalePrintView(LoginRequiredMixin, View):
    """Vista para generar e imprimir ticket térmico de venta"""

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        # Obtener la venta con sus relaciones
        sale = Sale.objects.select_related("patient").prefetch_related("details__exam").get(pk=pk)

        # Renderizar el template HTML del ticket
        html_string = render_to_string("admissions/ticket_print.html", {"sale": sale})

        # Generar PDF con WeasyPrint con codificación UTF-8 explícita
        pdf = HTML(string=html_string, encoding="utf-8").write_pdf(presentational_hints=True, optimize_size=("fonts",))

        # Devolver el PDF como respuesta
        response = HttpResponse(pdf, content_type="application/pdf; charset=utf-8")
        response["Content-Disposition"] = f'inline; filename="ticket_{sale.id}.pdf"'

        return response


@require_POST
def create_sale_api(request):
    """API endpoint para crear una venta con sus detalles"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "No autenticado"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # Validar datos requeridos
    patient_id = data.get("patient_id")
    observations = data.get("observations", "")
    exam_details = data.get("exam_details", [])

    if not patient_id:
        return JsonResponse({"error": "El paciente es requerido"}, status=400)

    if not exam_details or len(exam_details) == 0:
        return JsonResponse({"error": "Debe agregar al menos un examen"}, status=400)

    # Validar que el paciente existe
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

    # Validar exam_details
    validated_details = []
    for detail in exam_details:
        exam_id = detail.get("exam_id")
        price = detail.get("price")

        if not exam_id or price is None:
            return JsonResponse({"error": "Cada examen debe tener id y precio"}, status=400)

        # Validar que el examen existe
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return JsonResponse({"error": f"Examen con ID {exam_id} no encontrado"}, status=404)

        # Validar que el precio es un decimal válido
        try:
            price_decimal = Decimal(str(price))
            if price_decimal < 0:
                return JsonResponse({"error": "El precio no puede ser negativo"}, status=400)
            # Validar que tiene máximo 2 decimales
            if price_decimal.as_tuple().exponent < -2:
                return JsonResponse({"error": "El precio debe tener máximo 2 decimales"}, status=400)
        except (InvalidOperation, ValueError):
            return JsonResponse({"error": "Precio inválido"}, status=400)

        validated_details.append({"exam": exam, "price": price_decimal})

    # Crear la venta y sus detalles en una transacción
    try:
        with transaction.atomic():
            sale = Sale.objects.create(patient=patient, observations=observations)

            for detail in validated_details:
                SaleDetail.objects.create(sale=sale, exam=detail["exam"], price=detail["price"])

        # Agregar mensaje de éxito a la sesión
        messages.success(request, f"Venta #{sale.id} creada exitosamente")

        return JsonResponse({"success": True, "sale_id": sale.id, "message": "Venta creada exitosamente"}, status=201)

    except Exception as e:
        return JsonResponse({"error": f"Error al crear la venta: {str(e)}"}, status=500)
