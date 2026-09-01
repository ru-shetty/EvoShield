from django.urls import path

from .views import SecurityAuditView


urlpatterns = [
    path(
        "security-audit/",
        SecurityAuditView.as_view(),
        name="security-audit",
    ),
]