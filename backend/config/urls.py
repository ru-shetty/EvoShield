"""
Main EvoShield URL configuration.
"""

from django.urls import include, path
from backend.api.v1.views import (
    call_monitor_start,
    call_monitor_status,
    call_monitor_stop,
    dashboard,
    finalize_agent_scan,
    scan,
    scan_history,
)


urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/v1/scan/", scan, name="scan"),
    path("api/v1/scans/<str:entity_id>/finalize/", finalize_agent_scan, name="finalize-agent-scan"),
    path("api/v1/scans/", scan_history, name="scan-history"),
    path("api/v1/call-monitor/", call_monitor_status, name="call-monitor-status"),
    path("api/v1/call-monitor/start/", call_monitor_start, name="call-monitor-start"),
    path("api/v1/call-monitor/stop/", call_monitor_stop, name="call-monitor-stop"),
    path(
        "api/v1/",
        include("backend.api.v1.urls"),
    ),
]
