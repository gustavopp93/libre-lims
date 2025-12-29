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
    CreateExamCategoryView,
    CreateExamView,
    ExamCategoriesListView,
    ExamsDownloadTemplateView,
    ExamsListView,
    ExamsUploadView,
    UpdateExamCategoryView,
    UpdateExamView,
    search_exams_api,
)
from apps.orders.views import (
    CreateOrderView,
    CreateReferralOrderView,
    OrderDetailView,
    OrderPrintView,
    OrderResultsFormView,
    OrdersListView,
    cancel_order,
    complete_order,
    create_order_api,
    create_referral_order_api,
    download_orders_excel,
    search_referrals_api,
)
from apps.patients.views import (
    CreateLeadSourceView,
    CreatePatientView,
    DashboardView,
    LeadSourceListView,
    LoginView,
    LogoutView,
    PatientsDownloadTemplateView,
    PatientsListView,
    PatientsUploadView,
    UpdateLeadSourceView,
    UpdatePatientView,
    patient_details_api,
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
    path("orders/download-excel/", download_orders_excel, name="orders_download_excel"),
    path("orders/<int:order_id>/cancel/", cancel_order, name="cancel_order"),
    path("orders/<int:order_id>/complete/", complete_order, name="complete_order"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/print/", OrderPrintView.as_view(), name="order_print"),
    path("orders/<int:pk>/results-form/", OrderResultsFormView.as_view(), name="order_results_form"),
    path("patients/", PatientsListView.as_view(), name="patients_list"),
    path("patients/create/", CreatePatientView.as_view(), name="patients_create"),
    path("patients/<int:pk>/update/", UpdatePatientView.as_view(), name="patients_update"),
    path("patients/upload/", PatientsUploadView.as_view(), name="patients_upload"),
    path("patients/download-template/", PatientsDownloadTemplateView.as_view(), name="patients_download_template"),
    path("lead-sources/", LeadSourceListView.as_view(), name="lead_sources_list"),
    path("lead-sources/create/", CreateLeadSourceView.as_view(), name="lead_sources_create"),
    path("lead-sources/<int:pk>/update/", UpdateLeadSourceView.as_view(), name="lead_sources_update"),
    path("exams/", ExamsListView.as_view(), name="exams_list"),
    path("exams/create/", CreateExamView.as_view(), name="exams_create"),
    path("exams/<int:pk>/update/", UpdateExamView.as_view(), name="exams_update"),
    path("exams/upload/", ExamsUploadView.as_view(), name="exams_upload"),
    path("exams/download-template/", ExamsDownloadTemplateView.as_view(), name="exams_download_template"),
    path("exam-categories/", ExamCategoriesListView.as_view(), name="exam_categories_list"),
    path("exam-categories/create/", CreateExamCategoryView.as_view(), name="exam_categories_create"),
    path("exam-categories/<int:pk>/update/", UpdateExamCategoryView.as_view(), name="exam_categories_update"),
    path("api/patients/search/", search_patient_api, name="api_patient_search"),
    path("api/patients/details/", patient_details_api, name="api_patient_details"),
    path("api/exams/search/", search_exams_api, name="api_exams_search"),
    path("api/orders/create/", create_order_api, name="api_orders_create"),
    path("api/orders/referral/create/", create_referral_order_api, name="api_referral_orders_create"),
    path("api/referrals/search/", search_referrals_api, name="api_referrals_search"),
    path("company/", include("apps.billing.urls")),
    path("pricing/", include("apps.pricing.urls")),
]
