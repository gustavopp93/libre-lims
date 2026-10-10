from django.db import models

from apps.core.models import AuditMixin, TimeStampedMixin
from apps.exams.models import Exam


class Quote(TimeStampedMixin, AuditMixin):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CONVERTED = "converted", "Convertida"

    code = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Código de Cotización")
    coupon = models.ForeignKey(
        "pricing.Coupon",
        on_delete=models.PROTECT,
        related_name="quotes",
        null=True,
        blank=True,
        verbose_name="Cupón",
    )
    observations = models.TextField(blank=True, default="", verbose_name="Observaciones")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Estado")

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f"Cotización {self.code}"

    @property
    def total(self):
        return sum(detail.price for detail in self.details.all())


class QuoteDetail(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="details", verbose_name="Cotización")
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="quote_details", verbose_name="Examen")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    class Meta:
        verbose_name = "Detalle de Cotización"
        verbose_name_plural = "Detalles de Cotización"

    def __str__(self):
        return f"{self.exam.name} - S/. {self.price}"
