import json
import logging
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView, TemplateView
from weasyprint import HTML

from apps.billing.models import Company
from apps.exams.models import Exam
from apps.orders.models import Order, OrderDetail
from apps.patients.models import Patient
from apps.referrals.models import Referral

logger = logging.getLogger(__name__)


class OrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/orders_list.html"
    context_object_name = "orders"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        from datetime import datetime

        from django.utils import timezone

        queryset = Order.objects.select_related("patient", "referral")

        # Filtrar por tipo de documento
        document_type = self.request.GET.get("document_type")
        if document_type:
            queryset = queryset.filter(patient__document_type=document_type)

        # Filtrar por número de documento
        document_number = self.request.GET.get("document_number")
        if document_number:
            queryset = queryset.filter(patient__document_number__icontains=document_number)

        # Filtrar por rango de fechas
        date_from = self.request.GET.get("date_from")
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                date_from_aware = timezone.make_aware(datetime.combine(date_from_obj.date(), datetime.min.time()))
                queryset = queryset.filter(created_at__gte=date_from_aware)
            except ValueError:
                pass

        date_to = self.request.GET.get("date_to")
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                date_to_aware = timezone.make_aware(datetime.combine(date_to_obj.date(), datetime.max.time()))
                queryset = queryset.filter(created_at__lte=date_to_aware)
            except ValueError:
                pass

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["document_type"] = self.request.GET.get("document_type", "")
        context["document_number"] = self.request.GET.get("document_number", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        return context


class CreateOrderView(LoginRequiredMixin, TemplateView):
    template_name = "orders/create_order.html"
    login_url = reverse_lazy("login")


class CreateReferralOrderView(LoginRequiredMixin, TemplateView):
    template_name = "orders/referral_order_create.html"
    login_url = reverse_lazy("login")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Order.objects.select_related("patient").prefetch_related("details__exam")


class OrderPrintView(LoginRequiredMixin, View):
    """Vista para generar e imprimir ticket de orden"""

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        # Obtener la orden con sus relaciones
        order = Order.objects.select_related("patient").prefetch_related("details__exam").get(pk=pk)

        # Obtener la información de la compañía
        company = Company.objects.first()

        # Renderizar el template HTML del ticket
        html_string = render_to_string("orders/order_print.html", {"order": order, "company": company})

        # Generar PDF con WeasyPrint con codificación UTF-8 explícita
        pdf = HTML(string=html_string, encoding="utf-8").write_pdf(presentational_hints=True, optimize_size=("fonts",))

        # Devolver el PDF como respuesta
        response = HttpResponse(pdf, content_type="application/pdf; charset=utf-8")
        response["Content-Disposition"] = f'inline; filename="order_{order.id}.pdf"'

        return response


class OrderResultsFormView(LoginRequiredMixin, View):
    """Vista para generar formulario de resultados en A4 para completar a mano"""

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        # Obtener la orden con sus relaciones
        order = Order.objects.select_related("patient").prefetch_related("details__exam").get(pk=pk)

        # Obtener la información de la compañía
        company = Company.objects.first()

        # Renderizar el template HTML del formulario
        html_string = render_to_string("orders/order_results_form.html", {"order": order, "company": company})

        # Generar PDF con WeasyPrint
        pdf = HTML(string=html_string, encoding="utf-8").write_pdf(presentational_hints=True, optimize_size=("fonts",))

        # Devolver el PDF como respuesta
        response = HttpResponse(pdf, content_type="application/pdf; charset=utf-8")
        response["Content-Disposition"] = f'inline; filename="resultados_orden_{order.id}.pdf"'

        return response


@login_required
@require_POST
def create_order_api(request):
    """API endpoint para crear una orden con sus detalles"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # Validar datos requeridos
    patient_id = data.get("patient_id")
    coupon_code = data.get("coupon_code", "").strip()
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

    # Validar cupón si se proporcionó
    coupon = None
    if coupon_code:
        from apps.pricing.services import PricingService

        validation_result = PricingService.validate_coupon(coupon_code)

        if not validation_result["valid"]:
            return JsonResponse({"error": validation_result["error"]}, status=400)

        # Si el cupón es válido, obtenerlo de la base de datos
        from apps.pricing.models import Coupon

        coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)

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

    # Crear la orden y sus detalles en una transacción
    try:
        with transaction.atomic():
            order = Order.objects.create(patient=patient, coupon=coupon, observations=observations)

            for detail in validated_details:
                OrderDetail.objects.create(order=order, exam=detail["exam"], price=detail["price"])

        # Agregar mensaje de éxito a la sesión
        messages.success(request, f"Orden {order.code} creada exitosamente")

        return JsonResponse(
            {"success": True, "order_id": order.id, "order_code": order.code, "message": "Orden creada exitosamente"},
            status=201,
        )

    except Exception as e:
        logger.exception("Error al crear la orden")
        return JsonResponse({"error": f"Error al crear la orden: {str(e)}"}, status=500)


@login_required
@require_GET
def search_referrals_api(request):
    """API endpoint para buscar referidos"""
    query = request.GET.get("query", "").strip()

    if len(query) < 2:
        return JsonResponse({"referrals": []})

    # Buscar por nombre de negocio o RUC
    referrals = Referral.objects.filter(is_active=True).filter(
        models.Q(business_name__icontains=query) | models.Q(document_number__icontains=query)
    )[:10]

    referrals_data = [
        {
            "id": ref.id,
            "business_name": ref.business_name,
            "document_number": ref.document_number,
            "price_list_id": ref.price_list_id,
            "price_list_name": ref.price_list.name,
            "phone_number": ref.phone_number or "",
            "email": ref.email or "",
            "address": ref.address or "",
        }
        for ref in referrals
    ]

    return JsonResponse({"referrals": referrals_data})


@login_required
@require_POST
def create_referral_order_api(request):
    """API endpoint para crear una orden de referido con sus detalles"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # Validar datos requeridos
    referral_id = data.get("referral_id")
    patient_id = data.get("patient_id")
    observations = data.get("observations", "")
    exam_details = data.get("exam_details", [])

    if not referral_id:
        return JsonResponse({"error": "El referido es requerido"}, status=400)

    if not patient_id:
        return JsonResponse({"error": "El paciente es requerido"}, status=400)

    if not exam_details or len(exam_details) == 0:
        return JsonResponse({"error": "Debe agregar al menos un examen"}, status=400)

    # Validar que el referido existe y está activo
    try:
        referral = Referral.objects.get(id=referral_id, is_active=True)
    except Referral.DoesNotExist:
        return JsonResponse({"error": "Referido no encontrado o inactivo"}, status=404)

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
            if price_decimal.as_tuple().exponent < -2:
                return JsonResponse({"error": "El precio debe tener máximo 2 decimales"}, status=400)
        except (InvalidOperation, ValueError):
            return JsonResponse({"error": "Precio inválido"}, status=400)

        validated_details.append({"exam": exam, "price": price_decimal})

    # Crear la orden y sus detalles en una transacción
    try:
        with transaction.atomic():
            order = Order.objects.create(patient=patient, referral=referral, observations=observations)

            for detail in validated_details:
                OrderDetail.objects.create(order=order, exam=detail["exam"], price=detail["price"])

        messages.success(request, f"Orden de referido {order.code} creada exitosamente")

        return JsonResponse(
            {"success": True, "order_id": order.id, "order_code": order.code, "message": "Orden creada exitosamente"},
            status=201,
        )

    except Exception as e:
        logger.exception("Error al crear la orden de referido")
        return JsonResponse({"error": f"Error al crear la orden: {str(e)}"}, status=500)


@login_required
@require_POST
def cancel_order(request, order_id):
    """Anular una orden"""
    try:
        order = Order.objects.get(id=order_id)

        if order.status != Order.Status.PENDING:
            return JsonResponse({"error": "Solo se pueden anular órdenes pendientes"}, status=400)

        order.status = Order.Status.VOIDED
        order.save()

        return JsonResponse({"success": True, "message": "Orden anulada exitosamente"})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Orden no encontrada"}, status=404)
    except Exception as e:
        logger.exception("Error al anular la orden")
        return JsonResponse({"error": f"Error al anular la orden: {str(e)}"}, status=500)


@login_required
@require_POST
def complete_order(request, order_id):
    """Registrar pago de una orden"""
    try:
        order = Order.objects.get(id=order_id)

        if order.status != Order.Status.PENDING:
            return JsonResponse({"error": "Solo se pueden registrar pagos de órdenes pendientes"}, status=400)

        payment_method = request.POST.get("payment_method")

        if not payment_method:
            return JsonResponse({"error": "Debe especificar un método de pago"}, status=400)

        if payment_method not in dict(Order.PaymentMethod.choices):
            return JsonResponse({"error": "Método de pago inválido"}, status=400)

        order.status = Order.Status.PAID
        order.payment_method = payment_method
        order.save()

        return JsonResponse({"success": True, "message": "Pago registrado exitosamente"})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Orden no encontrada"}, status=404)
    except Exception as e:
        logger.exception("Error al completar la orden")
        return JsonResponse({"error": f"Error al completar la orden: {str(e)}"}, status=500)
