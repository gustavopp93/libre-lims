from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from apps.results.models import Result, ResultDetail
from apps.results.services import update_result_status


class ResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = "results/result_list.html"
    context_object_name = "results"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        from django.db import models

        queryset = Result.objects.select_related("order", "order__patient").prefetch_related("details")

        # Filtrar por estado general
        status = self.request.GET.get("status")
        if status in Result.ResultStatus.values:
            queryset = queryset.filter(status=status)

        # Filtrar por número de documento del paciente
        document_number = self.request.GET.get("document_number")
        if document_number:
            queryset = queryset.filter(order__patient__document_number__icontains=document_number)

        # Filtrar por nombre del paciente (first_name OR last_name)
        patient_name = self.request.GET.get("patient_name")
        if patient_name:
            queryset = queryset.filter(
                models.Q(order__patient__first_name__icontains=patient_name)
                | models.Q(order__patient__last_name__icontains=patient_name)
            )

        # Filtrar por código de orden
        order_code = self.request.GET.get("order_code")
        if order_code:
            queryset = queryset.filter(order__code__icontains=order_code)

        return queryset.order_by("-order__created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        context["status_choices"] = Result.ResultStatus.choices
        context["document_number"] = self.request.GET.get("document_number", "")
        context["patient_name"] = self.request.GET.get("patient_name", "")
        context["order_code"] = self.request.GET.get("order_code", "")
        return context


class ResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    template_name = "results/result_detail.html"
    context_object_name = "result"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Result.objects.select_related("order", "order__patient").prefetch_related(
            "details__exam", "details__order_detail"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verificar si todos los exámenes están entregados
        result = self.object
        all_delivered = all(detail.status == ResultDetail.ExamResultStatus.DELIVERED for detail in result.details.all())
        context["all_delivered"] = all_delivered
        return context

    def post(self, request, *args, **kwargs):
        """Procesar cambios de estado de los detalles"""
        result = self.get_object()

        # Procesar cada detalle
        for detail in result.details.all():
            # Obtener nuevo estado del form
            new_status = request.POST.get(f"detail_{detail.id}_status")
            if new_status and new_status != detail.status:
                # Validar que la transición es válida
                allowed_statuses = [status for status, label in detail.get_allowed_transitions()]
                if new_status in allowed_statuses:
                    detail.status = new_status
                    detail.save()

        # Recalcular estado general del resultado
        update_result_status(result)

        messages.success(request, "Estados actualizados exitosamente")
        return redirect("result_detail", pk=result.pk)
