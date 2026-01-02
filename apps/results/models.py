from django.db import models

from apps.core.models import TimeStampedModel


class Result(TimeStampedModel):
    """Resultado general de una orden"""

    class ResultStatus(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En Proceso"
        PARTIAL_RESULTS = "partial_results", "Resultados Parciales"
        COMPLETED = "completed", "Completado"
        PARTIAL_DELIVERY = "partial_delivery", "Entrega Parcial"
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
        default=ResultStatus.PENDING,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"

    def __str__(self):
        return f"Resultado {self.order.code} - {self.get_status_display()}"


class ResultDetail(TimeStampedModel):
    """Detalle de resultado por examen"""

    class ExamResultStatus(models.TextChoices):
        PENDING_SAMPLE = "pending_sample", "Pendiente de Muestra"
        SAMPLE_RECEIVED = "sample_received", "Muestra Recibida"
        INTERNAL_ANALYSIS = "internal_analysis", "En Análisis Interno"
        SENT_EXTERNAL = "sent_external", "Enviado a Lab Externo"
        RECEIVED_EXTERNAL = "received_external", "Recibido de Lab Externo"
        COMPLETED = "completed", "Completado"
        VALIDATED = "validated", "Validado"
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
        Retorna las transiciones válidas desde el estado actual.
        Permite saltar a cualquier estado posterior en el flujo.
        """
        # Orden de los estados en el flujo (índice determina si es "posterior")
        STATUS_ORDER = [
            self.ExamResultStatus.PENDING_SAMPLE,
            self.ExamResultStatus.SAMPLE_RECEIVED,
            self.ExamResultStatus.INTERNAL_ANALYSIS,  # Rama in-house
            self.ExamResultStatus.SENT_EXTERNAL,  # Rama tercerizado
            self.ExamResultStatus.RECEIVED_EXTERNAL,  # Rama tercerizado
            self.ExamResultStatus.COMPLETED,
            self.ExamResultStatus.VALIDATED,
            self.ExamResultStatus.DELIVERED,
        ]

        # Encontrar posición actual
        try:
            current_index = STATUS_ORDER.index(self.status)
        except ValueError:
            # Si el estado no está en la lista, solo permitir el actual
            return [(self.status, self.ExamResultStatus(self.status).label)]

        # Casos especiales según el estado actual
        if self.status == self.ExamResultStatus.PENDING_SAMPLE:
            # Desde PENDING_SAMPLE puede ir a cualquier estado posterior
            allowed = STATUS_ORDER[current_index:]
        elif self.status == self.ExamResultStatus.SAMPLE_RECEIVED:
            # Puede elegir rama in-house o tercerizado, y cualquier estado posterior
            allowed = [
                self.ExamResultStatus.SAMPLE_RECEIVED,
                self.ExamResultStatus.INTERNAL_ANALYSIS,
                self.ExamResultStatus.SENT_EXTERNAL,
                self.ExamResultStatus.COMPLETED,
                self.ExamResultStatus.VALIDATED,
                self.ExamResultStatus.DELIVERED,
            ]
        elif self.status == self.ExamResultStatus.INTERNAL_ANALYSIS:
            # Rama in-house: puede saltar directamente a estados finales
            allowed = [
                self.ExamResultStatus.INTERNAL_ANALYSIS,
                self.ExamResultStatus.COMPLETED,
                self.ExamResultStatus.VALIDATED,
                self.ExamResultStatus.DELIVERED,
            ]
        elif self.status == self.ExamResultStatus.SENT_EXTERNAL:
            # Rama tercerizado: debe pasar por RECEIVED_EXTERNAL
            allowed = [
                self.ExamResultStatus.SENT_EXTERNAL,
                self.ExamResultStatus.RECEIVED_EXTERNAL,
                self.ExamResultStatus.COMPLETED,
                self.ExamResultStatus.VALIDATED,
                self.ExamResultStatus.DELIVERED,
            ]
        elif self.status == self.ExamResultStatus.RECEIVED_EXTERNAL:
            # Después de recibir externo, cualquier estado final
            allowed = [
                self.ExamResultStatus.RECEIVED_EXTERNAL,
                self.ExamResultStatus.COMPLETED,
                self.ExamResultStatus.VALIDATED,
                self.ExamResultStatus.DELIVERED,
            ]
        elif self.status in [
            self.ExamResultStatus.COMPLETED,
            self.ExamResultStatus.VALIDATED,
            self.ExamResultStatus.DELIVERED,
        ]:
            # Estados finales: solo puede avanzar o mantener
            allowed = STATUS_ORDER[current_index:]
        else:
            # Por defecto: estado actual y posteriores
            allowed = STATUS_ORDER[current_index:]

        return [(status, self.ExamResultStatus(status).label) for status in allowed]
