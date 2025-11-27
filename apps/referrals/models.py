from django.core.exceptions import ValidationError
from django.db import models


class Referral(models.Model):
    business_name = models.CharField(max_length=200, verbose_name="Business Name")
    document_number = models.CharField(max_length=11, unique=True, verbose_name="RUC")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Address")
    price_list = models.ForeignKey(
        "pricing.PriceList",
        on_delete=models.PROTECT,
        related_name="referrals",
        verbose_name="Price List",
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"

    def __str__(self):
        return f"{self.business_name} - {self.document_number}"

    def clean(self):
        """Validate document number length"""
        if len(self.document_number) != 11:
            raise ValidationError({"document_number": "RUC must be exactly 11 characters"})
