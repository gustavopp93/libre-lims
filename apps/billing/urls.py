from django.urls import path

from .views import CompanyCreateView, CompanySettingsView

urlpatterns = [
    path("settings/", CompanySettingsView.as_view(), name="company_settings"),
    path("create/", CompanyCreateView.as_view(), name="company_create"),
]
