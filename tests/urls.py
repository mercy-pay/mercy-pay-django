from django.urls import include, path

urlpatterns = [path("webhooks/mercy-pay/", include("mercypay_django.urls"))]
