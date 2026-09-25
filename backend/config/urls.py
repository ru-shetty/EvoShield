"""
Main EvoShield URL configuration.
"""

from django.urls import include, path
from backend.api.v1.views import dashboard, scan, scan_history


urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/v1/scan/", scan, name="scan"),
    path("api/v1/scans/", scan_history, name="scan-history"),
    path(
        "api/v1/",
        include("backend.api.v1.urls"),
    ),
]
