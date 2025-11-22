from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("business_name", "document_number", "phone_number", "email")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        # Only allow adding if no company exists
        return not Company.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Never allow deletion
        return False
