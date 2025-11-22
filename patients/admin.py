from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "document_type", "document_number", "gender", "phone", "birthdate"]
    search_fields = ["last_name", "first_name", "document_number", "phone"]
    list_filter = ["document_type", "gender"]
