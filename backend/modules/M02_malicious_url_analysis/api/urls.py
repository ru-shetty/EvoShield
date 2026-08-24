"""
URL routes for M02 - Malicious URL Analysis.
"""

from django.urls import path

from .views import MaliciousURLAnalysisView


urlpatterns = [
    path(
        "analyze/",
        MaliciousURLAnalysisView.as_view(),
        name="malicious-url-analyze",
    ),
]