from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView

from apps.results.models import Result


class ResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = "results/result_list.html"
    context_object_name = "results"
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        queryset = Result.objects.select_related("order", "order__patient").prefetch_related("details")

        # Filtrar por estado
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filtrar por número de documento del paciente
        document_number = self.request.GET.get("document_number")
        if document_number:
            queryset = queryset.filter(order__patient__document_number__icontains=document_number)

        # Filtrar por código de orden
        order_code = self.request.GET.get("order_code")
        if order_code:
            queryset = queryset.filter(order__code__icontains=order_code)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        context["document_number"] = self.request.GET.get("document_number", "")
        context["order_code"] = self.request.GET.get("order_code", "")
        context["status_choices"] = Result.ResultStatus.choices
        return context
