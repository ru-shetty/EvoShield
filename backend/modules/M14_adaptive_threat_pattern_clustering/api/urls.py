from django.urls import path

from .views import (
    ProcessFeatureBatchView,
    ClusterStatisticsView,
    ResetClusterView,
)


urlpatterns = [

    path(
        "process/",
        ProcessFeatureBatchView.as_view(),
        name="m14-process"
    ),

    path(
        "statistics/",
        ClusterStatisticsView.as_view(),
        name="m14-statistics"
    ),

    path(
        "reset/",
        ResetClusterView.as_view(),
        name="m14-reset"
    ),
]