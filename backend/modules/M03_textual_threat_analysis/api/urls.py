"""
URL routes for M03 - Textual Threat Analysis.
"""

from django.urls import path

from .views import TextualThreatAnalysisView


urlpatterns = [
    path(
        "analyze/",
        TextualThreatAnalysisView.as_view(),
        name="textual-threat-analyze",
    ),
]