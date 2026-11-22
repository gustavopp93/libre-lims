from decimal import Decimal, InvalidOperation


class DiscountValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def validate_discount(raw_discount, subtotal):
    """Validate a discount amount against the subtotal and return it as Decimal.

    An empty value means no discount (0).
    """
    if raw_discount is None or str(raw_discount).strip() == "":
        return Decimal("0")

    try:
        discount = Decimal(str(raw_discount).strip())
    except (InvalidOperation, ValueError):
        raise DiscountValidationError("Descuento inválido") from None

    if not discount.is_finite():
        raise DiscountValidationError("Descuento inválido")
    if discount < 0:
        raise DiscountValidationError("El descuento no puede ser negativo")
    if discount.as_tuple().exponent < -2:
        raise DiscountValidationError("El descuento debe tener máximo 2 decimales")
    if discount > subtotal:
        raise DiscountValidationError(f"El descuento (S/. {discount}) no puede ser mayor al subtotal (S/. {subtotal})")

    return discount
