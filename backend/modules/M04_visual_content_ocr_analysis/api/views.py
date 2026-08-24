"""
API views for M04 - Visual Content OCR Analysis.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.service import VisualContentOCRAnalysisService
from .serializers import (
    OCRAnalysisRequestSerializer,
    OCRAnalysisResponseSerializer,
)


class VisualContentOCRAnalysisView(APIView):
    """
    API endpoint for visual content OCR analysis.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VisualContentOCRAnalysisService()

    def post(self, request, *args, **kwargs):
        """
        Analyze submitted OCR text.
        """

        request_serializer = OCRAnalysisRequestSerializer(
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
        ocr_confidence = request_serializer.validated_data[
            "ocr_confidence"
        ]

        try:
            analysis = self.service.analyze_text(
                text=text,
                ocr_confidence=ocr_confidence,
            )

            response_serializer = OCRAnalysisResponseSerializer(
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