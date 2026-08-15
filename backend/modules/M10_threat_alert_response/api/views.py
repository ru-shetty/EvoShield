from django.http import JsonResponse

from ..services.service import (
    create_alert_response
)


def threat_alert_view(request):

    sample_data = {
        "risk_level": "CRITICAL",
        "malware_detected": True,
        "digital_arrest_detected": True
    }

    return JsonResponse(
        create_alert_response(sample_data)
    )