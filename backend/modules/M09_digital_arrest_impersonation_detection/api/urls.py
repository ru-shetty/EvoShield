"""
Module 9 API URL configuration.
"""

from django.urls import path

from .views import analyze_digital_arrest


urlpatterns = [
    path(
        "digital-arrest/analyze/",
        analyze_digital_arrest,
        name="digital-arrest-analyze",
    ),
]