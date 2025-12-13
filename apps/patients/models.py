from django.db import models

from apps.core.models import TimeStampedModel


class LeadSource(TimeStampedModel):
    """Canal por el cual el cliente llegó al laboratorio"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, help_text="Orden de visualización")

    class Meta:
        verbose_name = "Canal de Adquisición"
        verbose_name_plural = "Canales de Adquisición"

    def __str__(self):
        return self.name


class Patient(TimeStampedModel):
    class DocumentType(models.TextChoices):
        DNI = "DNI", "DNI"
        CE = "CE", "Carnet de Extranjería"
        PASAPORTE = "PASAPORTE", "Pasaporte"

    class Sex(models.TextChoices):
        MALE = "MALE", "Masculino"
        FEMALE = "FEMALE", "Femenino"

    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.DNI,
    )
    document_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField()
    sex = models.CharField(
        max_length=10,
        choices=Sex.choices,
    )
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True, null=True)
    lead_source = models.ForeignKey(
        LeadSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="¿Cómo nos conoció?",
        help_text="Canal por el cual el cliente llegó por primera vez",
    )

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.document_type} {self.document_number}"
