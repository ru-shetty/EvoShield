"""
DRF serializers for Module 14.
"""

from rest_framework import serializers


class FeatureVectorSerializer(
    serializers.Serializer
):

    entity_id = serializers.CharField(
        required=True
    )

    features = serializers.ListField(
        child=serializers.FloatField(),
        required=True,
        allow_empty=False
    )


class BatchProcessingSerializer(
    serializers.Serializer
):

    feature_vectors = FeatureVectorSerializer(
        many=True,
        required=True
    )


class ClusterAssignmentSerializer(
    serializers.Serializer
):

    entity_id = serializers.CharField()

    cluster_id = serializers.IntegerField()

    distance = serializers.FloatField()

    centroid = serializers.ListField()

    cluster_statistics = serializers.DictField()

    drift_detected = serializers.BooleanField()

    psi_score = serializers.FloatField()

    dist_zscore = serializers.FloatField()

    adwin_flagged = serializers.BooleanField()