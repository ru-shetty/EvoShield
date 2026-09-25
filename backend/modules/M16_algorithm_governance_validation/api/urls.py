from django.urls import path

from .views import (
    attach_versions,
    create_candidate,
    deploy_candidate,
    health,
    rollback,
    runtime_event,
)


urlpatterns = [
    path(
        "candidate/create/",
        create_candidate,
        name="m16-create-candidate",
    ),

    path(
        "candidate/deploy/",
        deploy_candidate,
        name="m16-deploy-candidate",
    ),

    path(
        "runtime/event/",
        runtime_event,
        name="m16-runtime-event",
    ),

    path(
        "health/",
        health,
        name="m16-health",
    ),

    path(
        "rollback/",
        rollback,
        name="m16-rollback",
    ),

    path(
        "analysis/attach-versions/",
        attach_versions,
        name="m16-attach-versions",
    ),
]