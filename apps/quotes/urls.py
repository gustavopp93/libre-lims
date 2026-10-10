from django.urls import path

from apps.quotes import views

urlpatterns = [
    path("", views.QuoteListView.as_view(), name="quote_list"),
    path("create/", views.QuoteCreateView.as_view(), name="quote_create"),
    path("<int:pk>/", views.QuoteDetailView.as_view(), name="quote_detail"),
    path("<int:pk>/convert/", views.QuoteConvertView.as_view(), name="quote_convert"),
    path("<int:pk>/print/", views.QuotePrintView.as_view(), name="quote_print"),
    # API Endpoints
    path("api/create/", views.QuoteCreateAPIView.as_view(), name="api_quote_create"),
    path("api/<int:pk>/convert/", views.QuoteConvertAPIView.as_view(), name="api_quote_convert"),
]
