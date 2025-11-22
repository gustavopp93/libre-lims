from django.contrib import admin

from .models import Sale, SaleDetail


class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["id", "patient", "created_at", "get_total"]
    list_filter = ["created_at"]
    search_fields = ["patient__first_name", "patient__last_name", "patient__document_number"]
    inlines = [SaleDetailInline]
    readonly_fields = ["created_at", "updated_at"]

    def get_total(self, obj):
        return f"S/. {obj.total}"

    get_total.short_description = "Total"


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = ["sale", "exam", "price"]
    list_filter = ["sale__created_at"]
