from django.conf import settings
from django.db import models


class TimeStampedMixin(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creacion")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualizacion")

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """
    Abstract base model that provides 'created_by' and 'updated_by' fields.
    The values must be set explicitly in the view or service.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
        blank=True,
        verbose_name="Creado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updated",
        null=True,
        blank=True,
        verbose_name="Actualizado por",
    )

    class Meta:
        abstract = True
