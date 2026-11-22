from django.db import models

from apps.core.models import TimeStampedMixin


class Result(TimeStampedMixin):
    """Resultado general de una orden"""

    class ResultStatus(models.TextChoices):
        PENDING_SAMPLE = "pending_sample", "Pendiente de Muestra"
        SAMPLE_RECEIVED = "sample_received", "Muestra Recibida"
        INTERNAL_IN_PROGRESS = "internal_in_progress", "En Proceso Interno"
        EXTERNAL_IN_PROGRESS = "external_in_progress", "En Proceso Externo"
        MIXED_IN_PROGRESS = "mixed_in_progress", "En Proceso Mixto"
        READY_TO_DELIVER = "ready_to_deliver", "Listo para Entregar"
        DELIVERED = "delivered", "Entregado"

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="result",
        verbose_name="Orden",
    )
    status = models.CharField(
        max_length=30,
        choices=ResultStatus.choices,
        default=ResultStatus.PENDING_SAMPLE,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"

    def __str__(self):
        return f"Resultado {self.order.code} - {self.get_status_display()}"

    def get_progress(self):
        """Cuenta los exámenes por estado. Usa los detalles precargados (prefetch_related)."""
        exam_status = ResultDetail.ExamResultStatus
        statuses = [detail.status for detail in self.details.all()]
        delivered = statuses.count(exam_status.DELIVERED)
        return {
            "total": len(statuses),
            "ready": statuses.count(exam_status.RESULT_READY) + delivered,
            "delivered": delivered,
            "internal": statuses.count(exam_status.INTERNAL_ANALYSIS),
            "external": statuses.count(exam_status.SENT_EXTERNAL),
            "sample_received": statuses.count(exam_status.SAMPLE_RECEIVED),
            "pending_sample": statuses.count(exam_status.PENDING_SAMPLE),
        }


class ResultDetail(TimeStampedMixin):
    """Detalle de resultado por examen"""

    class ExamResultStatus(models.TextChoices):
        PENDING_SAMPLE = "pending_sample", "Pendiente de Muestra"
        SAMPLE_RECEIVED = "sample_received", "Muestra Recibida"
        INTERNAL_ANALYSIS = "internal_analysis", "En Análisis Interno"
        SENT_EXTERNAL = "sent_external", "Enviado a Lab Externo"
        RESULT_READY = "result_ready", "Resultado Listo"
        DELIVERED = "delivered", "Entregado"

    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="Resultado",
    )
    order_detail = models.ForeignKey(
        "orders.OrderDetail",
        on_delete=models.PROTECT,
        related_name="result_details",
        verbose_name="Detalle de Orden",
    )
    exam = models.ForeignKey(
        "exams.Exam",
        on_delete=models.PROTECT,
        related_name="result_details",
        verbose_name="Examen",
    )
    status = models.CharField(
        max_length=30,
        choices=ExamResultStatus.choices,
        default=ExamResultStatus.PENDING_SAMPLE,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Detalle de Resultado"
        verbose_name_plural = "Detalles de Resultado"
        unique_together = [["order_detail", "exam"]]

    def __str__(self):
        return f"{self.exam.name} - {self.get_status_display()}"

    def get_allowed_transitions(self):
        """
        Retorna los estados válidos desde el estado actual (incluye el actual).
        Desde Muestra Recibida se elige la ruta: análisis interno o laboratorio externo.
        """
        status = self.ExamResultStatus
        transitions = {
            status.PENDING_SAMPLE: [
                status.PENDING_SAMPLE,
                status.SAMPLE_RECEIVED,
                status.INTERNAL_ANALYSIS,
                status.SENT_EXTERNAL,
                status.RESULT_READY,
                status.DELIVERED,
            ],
            status.SAMPLE_RECEIVED: [
                status.SAMPLE_RECEIVED,
                status.INTERNAL_ANALYSIS,
                status.SENT_EXTERNAL,
                status.RESULT_READY,
                status.DELIVERED,
            ],
            status.INTERNAL_ANALYSIS: [status.INTERNAL_ANALYSIS, status.RESULT_READY, status.DELIVERED],
            status.SENT_EXTERNAL: [status.SENT_EXTERNAL, status.RESULT_READY, status.DELIVERED],
            status.RESULT_READY: [status.RESULT_READY, status.DELIVERED],
            status.DELIVERED: [status.DELIVERED],
        }
        allowed = transitions.get(self.status, [self.status])
        return [(value, self.ExamResultStatus(value).label) for value in allowed]
