from django.urls import path

from .views import threat_alert_view

urlpatterns = [
    path(
        "threat-alert/",
        threat_alert_view,
        name="threat-alert"
    ),
]