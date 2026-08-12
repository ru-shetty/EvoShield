"""
Module 9: Digital Arrest & Impersonation Detection API Views
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..services.service import analyze_evidence
from .serializers import DigitalArrestRequest


@csrf_exempt
def analyze_digital_arrest(request):
    """
    Analyze submitted text for digital-arrest indicators.
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON request body."},
            status=400,
        )

    try:
        request_data = DigitalArrestRequest.from_dict(data)
    except ValueError as error:
        return JsonResponse(
            {"error": str(error)},
            status=400,
        )

    try:
        result = analyze_evidence(request_data.text)

        return JsonResponse(
            result,
            status=200,
        )

    except ValueError as error:
        return JsonResponse(
            {"error": str(error)},
            status=400,
        )

    except Exception as error:
        return JsonResponse(
            {
                "error": "Internal server error.",
                "details": str(error),
            },
            status=500,
        )