from django.db import models

from apps.exams.models import Exam
from apps.patients.models import Patient


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="orders")
    observations = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.id} - {self.patient.first_name} {self.patient.last_name}"

    @property
    def total(self):
        return sum(detail.price for detail in self.details.all())


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="order_details")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order Detail"
        verbose_name_plural = "Order Details"

    def __str__(self):
        return f"{self.exam.name} - S/. {self.price}"
