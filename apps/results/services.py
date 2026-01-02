"""
Services para manejo de resultados de laboratorio
"""

from apps.results.models import Result, ResultDetail


def create_result_for_order(order):
    """
    Crea un Result y sus ResultDetails para una orden pagada.

    Para cada OrderDetail:
    - Si el exam NO tiene componentes: crea 1 ResultDetail para ese exam
    - Si el exam SÍ tiene componentes (panel): crea 1 ResultDetail por cada componente

    Args:
        order: Instancia de Order

    Returns:
        Result: El resultado creado
    """
    # Crear el resultado principal
    result = Result.objects.create(order=order)

    # Iterar sobre cada detalle de la orden
    for order_detail in order.details.select_related("exam").prefetch_related("exam__components"):
        exam = order_detail.exam

        if exam.has_components:
            # Panel: crear ResultDetail por cada componente
            components = exam.component_items.select_related("component_exam").order_by("order")

            for component_item in components:
                ResultDetail.objects.create(
                    result=result,
                    order_detail=order_detail,
                    exam=component_item.component_exam,
                )
        else:
            # Examen simple: crear 1 ResultDetail
            ResultDetail.objects.create(
                result=result,
                order_detail=order_detail,
                exam=exam,
            )

    return result
