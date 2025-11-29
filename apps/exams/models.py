from django.db import models

from apps.core.models import TimeStampedModel


class Exam(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.name} - S/. {self.price}"
        return f"{self.name} - S/. {self.price}"
