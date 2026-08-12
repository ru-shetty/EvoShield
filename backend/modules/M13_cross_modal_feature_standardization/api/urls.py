# M13_cross_modal_feature_standardization/api/urls.py

from django.urls import path

from .views import (
    CrossModalFeatureStandardizationView
)


urlpatterns = [

    path(
        "standardize/",
        CrossModalFeatureStandardizationView.as_view(),
        name="m13-standardize"
    ),

]