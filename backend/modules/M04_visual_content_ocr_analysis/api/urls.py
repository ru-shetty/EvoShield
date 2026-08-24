"""
URL routes for M04 - Visual Content OCR Analysis.
"""

from django.urls import path

from .views import VisualContentOCRAnalysisView


urlpatterns = [
    path(
        "analyze/",
        VisualContentOCRAnalysisView.as_view(),
        name="visual-content-ocr-analyze",
    ),
]