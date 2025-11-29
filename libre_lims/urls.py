"""
URL configuration for libre_lims project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.http import JsonResponse
from django.urls import include, path

from apps.exams.views import (
    BulkUploadExamsView,
    CreateExamView,
    ExamsListView,
    UpdateExamView,
    search_exams_api,
)
from apps.orders.views import (
    CreateOrderView,
    CreateReferralOrderView,
    OrderDetailView,
    OrderPrintView,
    OrdersListView,
    create_order_api,
    create_referral_order_api,
    get_referral_patients_api,
    search_referrals_api,
)
from apps.patients.views import (
    CreateLeadSourceView,
    CreatePatientView,
    DashboardView,
    LeadSourceListView,
    LoginView,
    LogoutView,
    PatientsListView,
    UpdateLeadSourceView,
    UpdatePatientView,
    search_patient_api,
)


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", DashboardView.as_view(), name="dashboard"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/create/", CreateOrderView.as_view(), name="create_order"),
    path("orders/referral/create/", CreateReferralOrderView.as_view(), name="create_referral_order"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/print/", OrderPrintView.as_view(), name="order_print"),
    path("patients/", PatientsListView.as_view(), name="patients_list"),
    path("patients/create/", CreatePatientView.as_view(), name="patients_create"),
    path("patients/<int:pk>/update/", UpdatePatientView.as_view(), name="patients_update"),
    path("lead-sources/", LeadSourceListView.as_view(), name="lead_sources_list"),
    path("lead-sources/create/", CreateLeadSourceView.as_view(), name="lead_sources_create"),
    path("lead-sources/<int:pk>/update/", UpdateLeadSourceView.as_view(), name="lead_sources_update"),
    path("exams/", ExamsListView.as_view(), name="exams_list"),
    path("exams/create/", CreateExamView.as_view(), name="exams_create"),
    path("exams/<int:pk>/update/", UpdateExamView.as_view(), name="exams_update"),
    path("exams/bulk-upload/", BulkUploadExamsView.as_view(), name="bulk_upload_exams"),
    path("api/patients/search/", search_patient_api, name="api_patient_search"),
    path("api/exams/search/", search_exams_api, name="api_exams_search"),
    path("api/orders/create/", create_order_api, name="api_orders_create"),
    path("api/orders/referral/create/", create_referral_order_api, name="api_referral_orders_create"),
    path("api/referrals/search/", search_referrals_api, name="api_referrals_search"),
    path("api/referrals/patients/", get_referral_patients_api, name="api_referral_patients"),
    path("company/", include("apps.billing.urls")),
    path("pricing/", include("apps.pricing.urls")),
]
