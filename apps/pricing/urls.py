from django.urls import path

from apps.pricing import views

urlpatterns = [
    # Price List URLs
    path("price-lists/", views.PriceListListView.as_view(), name="price_list_list"),
    path("price-lists/create/", views.PriceListCreateView.as_view(), name="price_list_create"),
    path("price-lists/<int:pk>/", views.PriceListDetailView.as_view(), name="price_list_detail"),
    path("price-lists/<int:pk>/update/", views.PriceListUpdateView.as_view(), name="price_list_update"),
    path("price-lists/<int:pk>/download/", views.PriceListDownloadView.as_view(), name="price_list_download_base"),
    path(
        "price-lists/<int:pk>/download-template/",
        views.PriceListDownloadTemplateView.as_view(),
        name="price_list_download_template",
    ),
    path("price-lists/<int:pk>/upload/", views.PriceListUploadView.as_view(), name="price_list_upload"),
    # Coupon URLs
    path("coupons/", views.CouponListView.as_view(), name="coupon_list"),
    path("coupons/create/", views.CouponCreateView.as_view(), name="coupon_create"),
    path("coupons/<int:pk>/update/", views.CouponUpdateView.as_view(), name="coupon_update"),
    # Referral URLs
    path("referrals/", views.ReferralListView.as_view(), name="referral_list"),
    path("referrals/create/", views.ReferralCreateView.as_view(), name="referral_create"),
    path("referrals/<int:pk>/update/", views.ReferralUpdateView.as_view(), name="referral_update"),
]
