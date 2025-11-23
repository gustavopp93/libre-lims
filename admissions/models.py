from django.db import models

from exams.models import Exam
from patients.models import Patient


class Sale(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="sales")
    observations = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def __str__(self):
        return f"Sale #{self.id} - {self.patient.first_name} {self.patient.last_name}"

    @property
    def total(self):
        return sum(detail.price for detail in self.details.all())


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="details")
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="sale_details")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Sale Detail"
        verbose_name_plural = "Sale Details"

    def __str__(self):
        return f"{self.exam.name} - S/. {self.price}"
