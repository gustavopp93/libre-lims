from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class Company(TimeStampedModel):
    """Model to store company information. Only one company should exist."""

    business_name = models.CharField(max_length=200, verbose_name="Razon Social")
    document_number = models.CharField(max_length=11, unique=True, verbose_name="RUC")
    phone_number = models.CharField(max_length=20, verbose_name="Telefono")
    email = models.EmailField(verbose_name="Correo Electronico")
    legal_address = models.TextField(verbose_name="Direccion Legal")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresa"

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        """Ensure only one company exists"""
        if not self.pk and Company.objects.exists():
            raise ValidationError("Solo puede existir una empresa en el sistema")
        return super().save(*args, **kwargs)

    def clean(self):
        """Validate document number length"""
        if len(self.document_number) != 11:
            raise ValidationError({"document_number": "El RUC debe tener exactamente 11 caracteres"})
