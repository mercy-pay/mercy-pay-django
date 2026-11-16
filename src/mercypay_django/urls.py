from django.urls import path

from .views import webhook

app_name = "mercypay"

urlpatterns = [path("", webhook, name="webhook")]
