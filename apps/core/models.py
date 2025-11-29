from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creacion")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualizacion")

    class Meta:
        abstract = True
