"""
API serializers for M02 - Malicious URL Analysis.
"""

from rest_framework import serializers


class URLAnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer for URL analysis input.
    """

    url = serializers.URLField(
        required=True,
        allow_blank=False,
    )


class URLAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for URL analysis output.
    """

    entity_id = serializers.CharField()
    url = serializers.CharField()
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