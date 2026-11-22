from django.db import migrations

# Estados de examen que se unen en "Resultado Listo"
OLD_READY_STATUSES = ["completed", "validated", "received_external"]

# Copia fija de las reglas de apps.results.services.calculate_result_status.
# Las migraciones no deben importar código de la app, porque ese código puede cambiar después.


def calculate_result_status(exam_statuses):
    if not exam_statuses:
        return "pending_sample"

    remaining = [s for s in exam_statuses if s != "delivered"]
    if not remaining:
        return "delivered"
    if all(s == "result_ready" for s in remaining):
        return "ready_to_deliver"

    has_internal = "internal_analysis" in remaining
    has_external = "sent_external" in remaining
    if has_internal and has_external:
        return "mixed_in_progress"
    if has_internal:
        return "internal_in_progress"
    if has_external:
        return "external_in_progress"
    if "sample_received" in remaining:
        return "sample_received"
    return "pending_sample"


def forwards(apps, schema_editor):
    Result = apps.get_model("results", "Result")
    ResultDetail = apps.get_model("results", "ResultDetail")

    ResultDetail.objects.filter(status__in=OLD_READY_STATUSES).update(status="result_ready")

    for result in Result.objects.prefetch_related("details").iterator(chunk_size=500):
        new_status = calculate_result_status([detail.status for detail in result.details.all()])
        if result.status != new_status:
            Result.objects.filter(pk=result.pk).update(status=new_status)


class Migration(migrations.Migration):
    dependencies = [
        ("results", "0002_result_status_tracking"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
