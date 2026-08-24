"""
API views for M03 - Textual Threat Analysis.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.service import TextualThreatAnalysisService
from .serializers import (
    TextAnalysisRequestSerializer,
    TextAnalysisResponseSerializer,
)


class TextualThreatAnalysisView(APIView):
    """
    API endpoint for textual threat analysis.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TextualThreatAnalysisService()

    def post(self, request, *args, **kwargs):
        """
        Analyze submitted textual content.
        """

        request_serializer = TextAnalysisRequestSerializer(
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

        text = request_serializer.validated_data["text"]

        try:
            analysis = self.service.analyze_text(text)

            response_serializer = TextAnalysisResponseSerializer(
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