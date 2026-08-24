"""
API serializers for M04 - Visual Content OCR Analysis.
"""

from rest_framework import serializers


class OCRAnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer for visual content OCR analysis input.
    """

    text = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    ocr_confidence = serializers.FloatField(
        required=False,
        default=1.0,
        min_value=0.0,
        max_value=1.0,
    )


class OCRAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for visual content OCR analysis output.
    """

    entity_id = serializers.CharField()
    text = serializers.CharField()
    ocr_confidence = serializers.FloatField()
    score = serializers.FloatField()
    status = serializers.CharField()
    risk_level = serializers.CharField()

    indicators = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    features = serializers.DictField(
        required=False,
        default=dict,
    )