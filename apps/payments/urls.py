from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("cielo/authorize/", views.CieloAuthorizeView.as_view(), name="cielo-authorize"),
    path("cielo/capture/", views.CieloCaptureView.as_view(), name="cielo-capture"),
]
