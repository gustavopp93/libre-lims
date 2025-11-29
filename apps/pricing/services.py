from django.utils import timezone

from apps.exams.models import Exam
from apps.pricing.models import Coupon, PriceListItem
from apps.referrals.models import Referral


class PricingService:
    """Servicio para manejar la lógica de precios de exámenes"""

    @staticmethod
    def get_exam_price(exam_id: int, referral_id: int | None = None, coupon_code: str | None = None) -> dict:
        """
        Obtiene el precio de un examen considerando tarifario de referido o cupón.

        Orden de prioridad:
        1. Si hay cupón válido → precio del tarifario del cupón
        2. Si hay referido → precio del tarifario del referido
        3. Precio base del examen

        Args:
            exam_id: ID del examen
            referral_id: ID del referido (opcional)
            coupon_code: Código del cupón (opcional)

        Returns:
            dict con:
                - price: Decimal con el precio
                - source: 'coupon', 'price_list' o 'base'
                - price_list_id: ID del tarifario (si aplica)
                - coupon_code: Código del cupón (si aplica)

        Raises:
            Exam.DoesNotExist: Si el examen no existe
            Referral.DoesNotExist: Si el referido no existe
        """
        # Obtener el examen (lanzará excepción si no existe)
        exam = Exam.objects.get(id=exam_id)

        # Prioridad 1: Si hay cupón, intentar obtener precio del tarifario del cupón
        if coupon_code:
            try:
                coupon = Coupon.objects.select_related("price_list").get(code=coupon_code.upper(), is_active=True)

                # Validar fecha de expiración
                if coupon.expiration_date and coupon.expiration_date < timezone.now().date():
                    # Cupón expirado, continuar con las siguientes prioridades
                    pass
                else:
                    # Buscar el precio en el tarifario del cupón
                    price_item = PriceListItem.objects.get(price_list=coupon.price_list, exam=exam)

                    return {
                        "price": str(price_item.price),
                        "source": "coupon",
                        "price_list_id": coupon.price_list.id,
                        "price_list_name": coupon.price_list.name,
                        "coupon_code": coupon.code,
                    }
            except (Coupon.DoesNotExist, PriceListItem.DoesNotExist):
                # Si el cupón no existe o no tiene precio para este examen,
                # continuar con las siguientes prioridades
                pass

        # Prioridad 2: Si hay referido, buscar en su tarifario
        if referral_id:
            try:
                referral = Referral.objects.select_related("price_list").get(id=referral_id, is_active=True)

                # Buscar el precio en el tarifario del referido
                price_item = PriceListItem.objects.get(price_list=referral.price_list, exam=exam)

                return {
                    "price": str(price_item.price),
                    "source": "price_list",
                    "price_list_id": referral.price_list.id,
                    "price_list_name": referral.price_list.name,
                }
            except (Referral.DoesNotExist, PriceListItem.DoesNotExist):
                # Si el referido no existe o no tiene precio en su tarifario,
                # continuar para devolver el precio base
                pass

        # Prioridad 3: Precio base del examen
        return {"price": str(exam.price), "source": "base"}

    @staticmethod
    def validate_coupon(coupon_code: str) -> dict:
        """
        Valida si un cupón existe, está activo y no ha expirado.

        Args:
            coupon_code: Código del cupón a validar

        Returns:
            dict con:
                - valid: bool indicando si el cupón es válido
                - coupon: datos del cupón si es válido
                - error: mensaje de error si no es válido
        """
        try:
            coupon = Coupon.objects.select_related("price_list").get(code=coupon_code.upper(), is_active=True)

            # Validar fecha de expiración
            if coupon.expiration_date and coupon.expiration_date < timezone.now().date():
                return {"valid": False, "error": "El cupón ha expirado"}

            return {
                "valid": True,
                "coupon": {
                    "code": coupon.code,
                    "price_list_id": coupon.price_list.id,
                    "price_list_name": coupon.price_list.name,
                    "expiration_date": str(coupon.expiration_date) if coupon.expiration_date else None,
                },
            }
        except Coupon.DoesNotExist:
            return {"valid": False, "error": "Cupón no válido o inactivo"}
