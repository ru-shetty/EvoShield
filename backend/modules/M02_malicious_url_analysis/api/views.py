"""
API views for M02 - Malicious URL Analysis.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.service import MaliciousURLAnalysisService
from .serializers import (
    URLAnalysisRequestSerializer,
    URLAnalysisResponseSerializer,
)


class MaliciousURLAnalysisView(APIView):
    """
    API endpoint for malicious URL analysis.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MaliciousURLAnalysisService()

    def post(self, request, *args, **kwargs):
        """
        Analyze a submitted URL.
        """

        request_serializer = URLAnalysisRequestSerializer(
            data=request.data
        )

        if not request_serializer.is_valid():
            return Response(
                {
                    "status": "FAILED",
                    "errors": request_serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = request_serializer.validated_data["url"]

        try:
            analysis = self.service.analyze_url(url)

            response_serializer = URLAnalysisResponseSerializer(
                analysis.to_dict()
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "status": "FAILED",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )