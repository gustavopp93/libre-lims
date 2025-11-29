from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, FormView, ListView, RedirectView, TemplateView, UpdateView

from .forms import LeadSourceForm, LoginForm, PatientForm, PatientUpdateForm
from .models import LeadSource, Patient


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            auth_login(self.request, user)
            messages.success(self.request, "Inicio de sesión exitoso")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Usuario o contraseña incorrectos")
            return self.form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = reverse_lazy("login")


class LogoutView(RedirectView):
    permanent = False
    url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Sesión cerrada exitosamente")
        return super().get(request, *args, **kwargs)


class PatientsListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = "patients/patient_list.html"
    context_object_name = "patients"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por tipo de documento
        document_type = self.request.GET.get("document_type")
        if document_type:
            queryset = queryset.filter(document_type=document_type)

        # Filtrar por número de documento
        document_number = self.request.GET.get("document_number")
        if document_number:
            queryset = queryset.filter(document_number__icontains=document_number)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["document_type"] = self.request.GET.get("document_type", "")
        context["document_number"] = self.request.GET.get("document_number", "")
        context["breadcrumbs"] = [
            {"name": "Pacientes", "url": None},
        ]
        return context


class CreatePatientView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_create.html"
    login_url = reverse_lazy("login")

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("patients_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next", "")
        context["breadcrumbs"] = [
            {"name": "Pacientes", "url": reverse_lazy("patients_list")},
            {"name": "Crear Paciente", "url": None},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Paciente creado exitosamente")
        return super().form_valid(form)


class UpdatePatientView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientUpdateForm
    template_name = "patients/patient_update.html"
    success_url = reverse_lazy("patients_list")
    login_url = reverse_lazy("login")
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Pacientes", "url": reverse_lazy("patients_list")},
            {"name": f"Editar: {self.object.first_name} {self.object.last_name}", "url": None},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Paciente actualizado exitosamente")
        return super().form_valid(form)


class AdmissionView(LoginRequiredMixin, TemplateView):
    template_name = "patients/admission.html"
    login_url = reverse_lazy("login")


@require_GET
def search_patient_api(request):
    """API endpoint para buscar pacientes por tipo y número de documento o por query general"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "No autenticado"}, status=401)

    # Búsqueda nueva por query (nombre, apellido, documento)
    query = request.GET.get("query", "").strip()
    if query:
        if len(query) < 2:
            return JsonResponse({"patients": []})

        # Buscar por nombre, apellido o documento
        patients = Patient.objects.filter(
            models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query)
            | models.Q(document_number__icontains=query)
        )[:10]

        patients_data = [
            {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "document_type": patient.document_type,
                "document_number": patient.document_number,
            }
            for patient in patients
        ]

        return JsonResponse({"patients": patients_data})

    # Búsqueda antigua por tipo y número de documento (para compatibilidad)
    document_type = request.GET.get("document_type")
    document_number = request.GET.get("document_number")

    if not document_type or not document_number:
        return JsonResponse({"error": "Parámetros incompletos"}, status=400)

    try:
        patient = Patient.objects.get(document_type=document_type, document_number=document_number)
        return JsonResponse(
            {
                "found": True,
                "patient": {
                    "id": patient.id,
                    "document_type": patient.document_type,
                    "document_number": patient.document_number,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                },
            }
        )
    except Patient.DoesNotExist:
        return JsonResponse({"found": False, "message": "Paciente no encontrado"})


class LeadSourceListView(LoginRequiredMixin, ListView):
    model = LeadSource
    template_name = "patients/lead_source_list.html"
    context_object_name = "lead_sources"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return LeadSource.objects.all().order_by("order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Canales de Adquisición", "url": None},
        ]
        return context


class CreateLeadSourceView(LoginRequiredMixin, CreateView):
    model = LeadSource
    form_class = LeadSourceForm
    template_name = "patients/lead_source_create.html"
    success_url = reverse_lazy("lead_sources_list")
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Canales de Adquisición", "url": reverse_lazy("lead_sources_list")},
            {"name": "Crear Canal", "url": None},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Canal de adquisición creado exitosamente")
        return super().form_valid(form)


class UpdateLeadSourceView(LoginRequiredMixin, UpdateView):
    model = LeadSource
    form_class = LeadSourceForm
    template_name = "patients/lead_source_update.html"
    success_url = reverse_lazy("lead_sources_list")
    login_url = reverse_lazy("login")
    context_object_name = "lead_source"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"name": "Canales de Adquisición", "url": reverse_lazy("lead_sources_list")},
            {"name": f"Editar: {self.object.name}", "url": None},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Canal de adquisición actualizado exitosamente")
        return super().form_valid(form)
