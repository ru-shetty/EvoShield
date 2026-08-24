"""
API serializers for M03 - Textual Threat Analysis.
"""

from rest_framework import serializers


class TextAnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer for textual threat analysis input.
    """

    text = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class TextAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for textual threat analysis output.
    """

    entity_id = serializers.CharField()
    text = serializers.CharField()
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