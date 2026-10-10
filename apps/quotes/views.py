import json
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from weasyprint import HTML

from apps.billing.models import Company
from apps.patients.models import Patient
from apps.pricing.models import Coupon
from apps.pricing.services import PricingService
from apps.quotes.models import Quote
from apps.quotes.services import QuoteValidationError, convert_quote_to_order, create_quote, validate_exam_details

logger = logging.getLogger(__name__)


def _render_pdf(template_name, context):
    html_string = render_to_string(template_name, context)
    return HTML(string=html_string, encoding="utf-8").write_pdf(presentational_hints=True, optimize_size=("fonts",))


class QuoteListView(LoginRequiredMixin, ListView):
    model = Quote
    template_name = "quotes/quote_list.html"
    context_object_name = "quotes"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        queryset = Quote.objects.select_related("order").prefetch_related("details")

        code = self.request.GET.get("code")
        if code:
            queryset = queryset.filter(code__icontains=code)

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        date_from = self.request.GET.get("date_from")
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                queryset = queryset.filter(
                    created_at__gte=timezone.make_aware(datetime.combine(date_from_obj.date(), datetime.min.time()))
                )
            except ValueError:
                pass

        date_to = self.request.GET.get("date_to")
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                queryset = queryset.filter(
                    created_at__lte=timezone.make_aware(datetime.combine(date_to_obj.date(), datetime.max.time()))
                )
            except ValueError:
                pass

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["code"] = self.request.GET.get("code", "")
        context["status"] = self.request.GET.get("status", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["status_choices"] = Quote.Status.choices
        return context


class QuoteCreateView(LoginRequiredMixin, TemplateView):
    template_name = "quotes/quote_create.html"
    login_url = reverse_lazy("login")


class QuoteDetailView(LoginRequiredMixin, DetailView):
    model = Quote
    template_name = "quotes/quote_detail.html"
    context_object_name = "quote"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Quote.objects.select_related("coupon__price_list", "order", "created_by").prefetch_related(
            "details__exam"
        )


class QuoteConvertView(LoginRequiredMixin, DetailView):
    model = Quote
    template_name = "quotes/quote_convert.html"
    context_object_name = "quote"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Quote.objects.select_related("coupon__price_list").prefetch_related("details__exam")

    def get(self, request, *args, **kwargs):
        quote = self.get_object()
        if quote.status != Quote.Status.PENDING:
            messages.error(request, "Solo se pueden convertir cotizaciones pendientes")
            return redirect("quote_detail", pk=quote.pk)
        return super().get(request, *args, **kwargs)


class QuotePrintView(LoginRequiredMixin, View):
    """Ticket de cotización (sin datos del paciente)"""

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        quote = get_object_or_404(Quote.objects.prefetch_related("details__exam"), pk=pk)
        pdf = _render_pdf("quotes/quote_print.html", {"quote": quote, "company": Company.objects.first()})

        response = HttpResponse(pdf, content_type="application/pdf; charset=utf-8")
        response["Content-Disposition"] = f'inline; filename="cotizacion_{quote.code}.pdf"'
        return response


class QuoteFormPrintView(LoginRequiredMixin, View):
    """Formulario A4 de cotización (sin datos del paciente)"""

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        quote = get_object_or_404(Quote.objects.prefetch_related("details__exam"), pk=pk)
        pdf = _render_pdf("quotes/quote_form.html", {"quote": quote, "company": Company.objects.first()})

        response = HttpResponse(pdf, content_type="application/pdf; charset=utf-8")
        response["Content-Disposition"] = f'inline; filename="cotizacion_a4_{quote.code}.pdf"'
        return response


class QuoteCreateAPIView(LoginRequiredMixin, View):
    """API endpoint para crear una cotización con sus detalles"""

    login_url = reverse_lazy("login")
    http_method_names = ["post"]

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        coupon_code = data.get("coupon_code", "").strip()
        observations = data.get("observations", "")

        coupon = None
        if coupon_code:
            validation_result = PricingService.validate_coupon(coupon_code)
            if not validation_result["valid"]:
                return JsonResponse({"error": validation_result["error"]}, status=400)
            coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)

        try:
            validated_details = validate_exam_details(data.get("exam_details", []))
        except QuoteValidationError as e:
            return JsonResponse({"error": e.message}, status=e.status)

        try:
            quote = create_quote(
                coupon=coupon, observations=observations, validated_details=validated_details, user=request.user
            )
        except Exception as e:
            logger.exception("Error al crear la cotización")
            return JsonResponse({"error": f"Error al crear la cotización: {str(e)}"}, status=500)

        messages.success(request, f"Cotización {quote.code} creada exitosamente")
        return JsonResponse(
            {
                "success": True,
                "quote_id": quote.id,
                "quote_code": quote.code,
                "redirect_url": reverse("quote_detail", args=[quote.id]),
            },
            status=201,
        )


class QuoteConvertAPIView(LoginRequiredMixin, View):
    """API endpoint para convertir una cotización en orden asignando un paciente"""

    login_url = reverse_lazy("login")
    http_method_names = ["post"]

    def post(self, request, pk):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        patient_id = data.get("patient_id")
        if not patient_id:
            return JsonResponse({"error": "El paciente es requerido"}, status=400)

        try:
            patient = Patient.objects.get(id=patient_id)
        except (Patient.DoesNotExist, ValueError):
            return JsonResponse({"error": "Paciente no encontrado"}, status=404)

        try:
            order = convert_quote_to_order(quote_id=pk, patient=patient, user=request.user)
        except Quote.DoesNotExist:
            return JsonResponse({"error": "Cotización no encontrada"}, status=404)
        except QuoteValidationError as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except Exception as e:
            logger.exception("Error al convertir la cotización")
            return JsonResponse({"error": f"Error al convertir la cotización: {str(e)}"}, status=500)

        messages.success(request, f"Orden {order.code} generada desde la cotización {order.quote.code}")
        return JsonResponse(
            {
                "success": True,
                "order_id": order.id,
                "order_code": order.code,
                "redirect_url": reverse("order_detail", args=[order.id]),
            },
            status=201,
        )
