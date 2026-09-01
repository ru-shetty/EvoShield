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
    path(
        "",
        include(
            "backend.modules.M10_threat_alert_response.api.urls"
        ),
    ),
    path(
        "",
        include(
            "backend.modules.M11_security_monitoring_visualization.api.urls"
        ),
    ),
    path(
    "",
    include(
        "backend.modules.M12_security_data_audit_management.api.urls"
    ),
),
]