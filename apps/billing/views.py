from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from apps.billing.forms import CompanyForm
from apps.billing.models import Company


class CompanySettingsView(LoginRequiredMixin, UpdateView):
    """View to edit company settings. Redirects to create if company doesn't exist."""

    model = Company
    form_class = CompanyForm
    template_name = "billing/company_settings.html"
    success_url = reverse_lazy("company_settings")
    login_url = reverse_lazy("login")

    def get_object(self, queryset=None):
        """Get the single company instance, or redirect to create if it doesn't exist"""
        company = Company.objects.first()
        if not company:
            return None
        return company

    def get(self, request, *args, **kwargs):
        """Redirect to create view if company doesn't exist"""
        if not Company.objects.exists():
            return redirect("company_create")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Configuracion de empresa actualizada exitosamente")
        return super().form_valid(form)


class CompanyCreateView(LoginRequiredMixin, CreateView):
    """View to create company. Only accessible if no company exists."""

    model = Company
    form_class = CompanyForm
    template_name = "billing/company_create.html"
    success_url = reverse_lazy("company_settings")
    login_url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        """Redirect to settings if company already exists"""
        if Company.objects.exists():
            messages.warning(request, "La empresa ya esta configurada")
            return redirect("company_settings")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Empresa creada exitosamente")
        return super().form_valid(form)
