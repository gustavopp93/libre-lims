from django.db import models


class Patient(models.Model):
    class DocumentType(models.TextChoices):
        DNI = "DNI", "DNI"
        CE = "CE", "Carnet de Extranjería"
        PASAPORTE = "PASAPORTE", "Pasaporte"

    class Gender(models.TextChoices):
        MALE = "MALE", "Hombre"
        FEMALE = "FEMALE", "Mujer"

    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.DNI,
    )
    document_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.document_type} {self.document_number}"
