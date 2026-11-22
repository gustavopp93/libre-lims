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


def calculate_result_status(exam_statuses):
    """
    Calcula el estado general de un resultado a partir de los estados de sus exámenes.

    Reglas (en orden):
    1. Sin exámenes -> Pendiente de Muestra
    2. Todos entregados -> Entregado
    3. Los no entregados están todos con resultado listo -> Listo para Entregar
    4. Hay exámenes en proceso (sin contar entregados ni listos):
       - internos y externos -> En Proceso Mixto
       - solo internos -> En Proceso Interno
       - solo externos -> En Proceso Externo
    5. Hay muestras recibidas sin ruta -> Muestra Recibida
    6. En otro caso -> Pendiente de Muestra
    """
    exam_status = ResultDetail.ExamResultStatus
    result_status = Result.ResultStatus

    if not exam_statuses:
        return result_status.PENDING_SAMPLE

    remaining = [s for s in exam_statuses if s != exam_status.DELIVERED]
    if not remaining:
        return result_status.DELIVERED
    if all(s == exam_status.RESULT_READY for s in remaining):
        return result_status.READY_TO_DELIVER

    has_internal = exam_status.INTERNAL_ANALYSIS in remaining
    has_external = exam_status.SENT_EXTERNAL in remaining
    if has_internal and has_external:
        return result_status.MIXED_IN_PROGRESS
    if has_internal:
        return result_status.INTERNAL_IN_PROGRESS
    if has_external:
        return result_status.EXTERNAL_IN_PROGRESS
    if exam_status.SAMPLE_RECEIVED in remaining:
        return result_status.SAMPLE_RECEIVED
    return result_status.PENDING_SAMPLE


def update_result_status(result):
    """Recalcula y guarda el estado general del resultado. Llamar después de cambiar el estado de un examen."""
    exam_statuses = list(result.details.values_list("status", flat=True))
    result.status = calculate_result_status(exam_statuses)
    result.save(update_fields=["status", "updated_at"])
    return result
