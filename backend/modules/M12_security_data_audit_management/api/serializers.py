from rest_framework import serializers


class SecurityAuditSerializer(serializers.Serializer):

    entity_id = serializers.CharField()
    entity_type = serializers.CharField()

    feature_vector = serializers.ListField(
        child=serializers.FloatField()
    )

    cluster_id = serializers.IntegerField()

    trust_level = serializers.IntegerField()

    status = serializers.CharField()

    risk_history = serializers.ListField(
        child=serializers.IntegerField()
    )

    drift_events = serializers.ListField()

    rollback_logs = serializers.ListField()

    model_name = serializers.CharField()

    model_version = serializers.CharField()

    analysis_version = serializers.CharField()