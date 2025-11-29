from apps.billing.models import Company


def company_processor(request):
    """
    Context processor to make company information available in all templates.
    Returns the single company instance if it exists, None otherwise.
    """
    try:
        company = Company.objects.first()
    except Exception:
        company = None

    return {"company": company}
