from django.urls import path

from .views import MonitoringDashboardView


urlpatterns = [
    path(
        "monitoring-dashboard/",
        MonitoringDashboardView.as_view(),
        name="monitoring-dashboard",
    ),
]