from django.db import models
from django.utils import timezone

from apps.core.models import AuditMixin, TimeStampedMixin
from apps.exams.models import Exam
from apps.patients.models import Patient


class Order(TimeStampedMixin):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PAID = "paid", "Pagado"
        VOIDED = "voided", "Anulado"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Efectivo"
        BANK_TRANSFER = "bank_transfer", "Transferencia bancaria"
        CARD = "card", "Tarjeta"
        DIGITAL_WALLET = "digital_wallet", "Billeteras digitales"

    code = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Código de Orden")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="orders")
    referral = models.ForeignKey(
        "referrals.Referral",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="Referral",
    )
    coupon = models.ForeignKey(
        "pricing.Coupon",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="Coupon",
    )
    quote = models.OneToOneField(
        "quotes.Quote",
        on_delete=models.PROTECT,
        related_name="order",
        null=True,
        blank=True,
        verbose_name="Cotización",
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, null=True, blank=True, verbose_name="Método de Pago"
    )
    observations = models.TextField(blank=True, default="", verbose_name="Observaciones")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.code} - {self.patient.first_name} {self.patient.last_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_order_code()
        super().save(*args, **kwargs)

    def _generate_order_code(self):
        """Generate order code with format YYYYMMdd-000001"""
        # Get current date in configured timezone
        now = timezone.localtime(timezone.now())
        date_prefix = now.strftime("%Y%m%d")

        # Find the last order code for today
        last_order = Order.objects.filter(code__startswith=date_prefix).order_by("-code").first()

        if last_order:
            # Extract the sequence number and increment
            last_sequence = int(last_order.code.split("-")[1])
            new_sequence = last_sequence + 1
        else:
            # First order of the day
            new_sequence = 1

        # Format: YYYYMMdd-000001
        return f"{date_prefix}-{new_sequence:06d}"

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


class PaymentMethod(TimeStampedMixin):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return self.name


class Payment(TimeStampedMixin, AuditMixin):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments", verbose_name="Orden")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago {self.pk} - Orden {self.order.code}"

    @property
    def total(self):
        return sum(detail.amount for detail in self.details.all())


class PaymentDetail(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="details", verbose_name="Pago")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name="payment_details", verbose_name="Método de Pago"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")

    class Meta:
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"

    def __str__(self):
        return f"{self.payment_method.name} - S/. {self.amount}"
