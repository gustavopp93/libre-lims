from apps.exams.models import Exam
from apps.pricing.models import PriceListItem
from apps.referrals.models import Referral


class PricingService:
    """Servicio para manejar la lógica de precios de exámenes"""

    @staticmethod
    def get_exam_price(exam_id: int, referral_id: int | None = None) -> dict:
        """
        Obtiene el precio de un examen considerando tarifario de referido.

        Orden de prioridad:
        1. Si hay referido → precio del tarifario del referido
        2. Precio base del examen

        Args:
            exam_id: ID del examen
            referral_id: ID del referido (opcional)

        Returns:
            dict con:
                - price: Decimal con el precio
                - source: 'price_list' o 'base'
                - price_list_id: ID del tarifario (si aplica)

        Raises:
            Exam.DoesNotExist: Si el examen no existe
            Referral.DoesNotExist: Si el referido no existe
        """
        # Obtener el examen (lanzará excepción si no existe)
        exam = Exam.objects.get(id=exam_id)

        # Prioridad 1: Si hay referido, buscar en su tarifario
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

        # Prioridad 2: Precio base del examen
        return {"price": str(exam.price), "source": "base"}
