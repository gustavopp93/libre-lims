from django.db import models

from apps.core.models import TimeStampedModel


class ExamCategory(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Exam Category"
        verbose_name_plural = "Exam Categories"

    def __str__(self):
        return f"[{self.code}] {self.name}"


class Provider(TimeStampedModel):
    """Proveedor externo (laboratorio de referencia)"""

    name = models.CharField(max_length=200, unique=True)
    contact_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"

    def __str__(self):
        return self.name


class Exam(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        ExamCategory,
        on_delete=models.PROTECT,
        related_name="exams",
        null=True,
        blank=True,
    )

    # Campo para identificar si es un panel/perfil con componentes
    has_components = models.BooleanField(
        default=False, help_text="Marcar si este examen contiene otros exámenes (ej: perfiles, paneles)"
    )

    # Relación recursiva M2M para componentes
    components = models.ManyToManyField(
        "self",
        through="ExamComponent",
        through_fields=("parent_exam", "component_exam"),
        symmetrical=False,
        related_name="parent_exams",
        blank=True,
    )

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        panel_indicator = " [PANEL]" if self.has_components else ""
        if self.code:
            return f"[{self.code}] {self.name}{panel_indicator} - S/. {self.price}"
        return f"{self.name}{panel_indicator} - S/. {self.price}"


class ExamComponent(TimeStampedModel):
    """Tabla intermedia para componentes de un examen (panel)"""

    parent_exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="component_items", help_text="Examen padre (panel)"
    )
    component_exam = models.ForeignKey(
        Exam, on_delete=models.PROTECT, related_name="included_in_panels", help_text="Examen componente"
    )
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el panel")

    class Meta:
        unique_together = ["parent_exam", "component_exam"]
        verbose_name = "Exam Component"
        verbose_name_plural = "Exam Components"

    def __str__(self):
        return f"{self.parent_exam.name} → {self.component_exam.name} (orden: {self.order})"
