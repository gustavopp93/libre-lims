from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from apps.results.models import Result, ResultDetail


class ResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = "results/result_list.html"
    context_object_name = "results"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        from django.db import models

        queryset = Result.objects.select_related("order", "order__patient").prefetch_related("details")

        # Mapeo de grupos de status por color
        status_groups = {
            "pendiente": [Result.ResultStatus.PENDING],
            "en_progreso": [
                Result.ResultStatus.IN_PROGRESS,
                Result.ResultStatus.PARTIAL_RESULTS,
                Result.ResultStatus.COMPLETED,
                Result.ResultStatus.PARTIAL_DELIVERY,
            ],
            "entregado": [Result.ResultStatus.DELIVERED],
        }

        # Filtrar por grupo de estado (basado en color)
        status_group = self.request.GET.get("status_group")
        if status_group and status_group in status_groups:
            queryset = queryset.filter(status__in=status_groups[status_group])

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

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_group"] = self.request.GET.get("status_group", "")
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
        result = self.get_object()
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
        self._update_result_status(result)

        messages.success(request, "Estados actualizados exitosamente")
        return redirect("result_detail", pk=result.pk)

    def _update_result_status(self, result):
        """
        Actualiza el estado general del resultado basado en los estados de los detalles.
        La prioridad es de los estados más avanzados a los menos avanzados.
        """
        details = result.details.all()
        if not details.exists():
            return

        statuses = [d.status for d in details]

        # PRIORIDAD 1: Estados de entrega (más avanzados)
        # Todos entregados -> DELIVERED
        if all(s == ResultDetail.ExamResultStatus.DELIVERED for s in statuses):
            result.status = Result.ResultStatus.DELIVERED
        # Al menos uno entregado pero no todos -> PARTIAL_DELIVERY
        elif any(s == ResultDetail.ExamResultStatus.DELIVERED for s in statuses):
            result.status = Result.ResultStatus.PARTIAL_DELIVERY

        # PRIORIDAD 2: Estados de completado
        # Todos completados o validados (ninguno entregado) -> COMPLETED
        elif all(
            s in [ResultDetail.ExamResultStatus.COMPLETED, ResultDetail.ExamResultStatus.VALIDATED] for s in statuses
        ):
            result.status = Result.ResultStatus.COMPLETED
        # Algunos completados/validados pero no todos -> PARTIAL_RESULTS
        elif any(
            s in [ResultDetail.ExamResultStatus.COMPLETED, ResultDetail.ExamResultStatus.VALIDATED] for s in statuses
        ):
            result.status = Result.ResultStatus.PARTIAL_RESULTS

        # PRIORIDAD 3: Estados intermedios
        # Al menos uno en proceso -> IN_PROGRESS
        elif any(
            s
            in [
                ResultDetail.ExamResultStatus.SAMPLE_RECEIVED,
                ResultDetail.ExamResultStatus.INTERNAL_ANALYSIS,
                ResultDetail.ExamResultStatus.SENT_EXTERNAL,
                ResultDetail.ExamResultStatus.RECEIVED_EXTERNAL,
            ]
            for s in statuses
        ):
            result.status = Result.ResultStatus.IN_PROGRESS

        # PRIORIDAD 4: Estado inicial
        # Todos pendiente muestra -> PENDING
        elif all(s == ResultDetail.ExamResultStatus.PENDING_SAMPLE for s in statuses):
            result.status = Result.ResultStatus.PENDING

        result.save()
