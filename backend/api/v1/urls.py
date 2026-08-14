"""
API v1 URL configuration.
"""

from django.urls import include, path


urlpatterns = [
    path(
        "",
        include(
            "backend.modules.M09_digital_arrest_impersonation_detection.api.urls"
        ),
    ),
]