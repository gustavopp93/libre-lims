from django.db import models

from apps.exams.models import Exam


class PriceList(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Price List"
        verbose_name_plural = "Price Lists"

    def __str__(self):
        return self.name


class PriceListItem(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name="items", verbose_name="Price List")
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, verbose_name="Exam")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")

    class Meta:
        verbose_name = "Price List Item"
        verbose_name_plural = "Price List Items"
        unique_together = ["price_list", "exam"]

    def __str__(self):
        return f"{self.price_list.name} - {self.exam.name}: S/. {self.price}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.PROTECT,
        related_name="coupons",
        verbose_name="Price List",
    )
    expiration_date = models.DateField(null=True, blank=True, verbose_name="Expiration Date")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.code} - {self.price_list.name}"

    def save(self, *args, **kwargs):
        """Convert code to uppercase before saving"""
        self.code = self.code.upper()
        super().save(*args, **kwargs)
