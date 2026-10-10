from decimal import Decimal, InvalidOperation

from django.db import transaction

from apps.exams.models import Exam
from apps.orders.models import Order, OrderDetail
from apps.quotes.models import Quote, QuoteDetail


class QuoteValidationError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def generate_quote_code():
    """Generate a global autoincremental quote code with format 0000001"""
    last_quote = Quote.objects.order_by("-id").first()
    new_sequence = int(last_quote.code) + 1 if last_quote else 1

    return f"{new_sequence:07d}"


def validate_exam_details(exam_details):
    """Validate a list of {exam_id, price} dicts and return [{exam, price}]."""
    if not exam_details:
        raise QuoteValidationError("Debe agregar al menos un examen")

    validated_details = []
    for detail in exam_details:
        exam_id = detail.get("exam_id")
        price = detail.get("price")

        if not exam_id or price is None:
            raise QuoteValidationError("Cada examen debe tener id y precio")

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise QuoteValidationError(f"Examen con ID {exam_id} no encontrado", status=404) from None

        try:
            price_decimal = Decimal(str(price))
        except (InvalidOperation, ValueError):
            raise QuoteValidationError("Precio inválido") from None

        if not price_decimal.is_finite():
            raise QuoteValidationError("Precio inválido")
        if price_decimal < 0:
            raise QuoteValidationError("El precio no puede ser negativo")
        if price_decimal.as_tuple().exponent < -2:
            raise QuoteValidationError("El precio debe tener máximo 2 decimales")

        validated_details.append({"exam": exam, "price": price_decimal})

    return validated_details


def create_quote(*, coupon, observations, validated_details, user):
    with transaction.atomic():
        quote = Quote.objects.create(
            code=generate_quote_code(),
            coupon=coupon,
            observations=observations,
            created_by=user,
            updated_by=user,
        )
        QuoteDetail.objects.bulk_create(
            [QuoteDetail(quote=quote, exam=detail["exam"], price=detail["price"]) for detail in validated_details]
        )
    return quote


def convert_quote_to_order(*, quote_id, patient, user):
    """Create an Order from a pending Quote, keeping the quoted prices."""
    with transaction.atomic():
        quote = Quote.objects.select_for_update().get(id=quote_id)

        if quote.status != Quote.Status.PENDING:
            raise QuoteValidationError("Solo se pueden convertir cotizaciones pendientes")

        order = Order.objects.create(
            patient=patient,
            coupon=quote.coupon,
            observations=quote.observations,
            quote=quote,
        )
        OrderDetail.objects.bulk_create(
            [OrderDetail(order=order, exam=detail.exam, price=detail.price) for detail in quote.details.all()]
        )

        quote.status = Quote.Status.CONVERTED
        quote.updated_by = user
        quote.save(update_fields=["status", "updated_by", "updated_at"])

    return order
