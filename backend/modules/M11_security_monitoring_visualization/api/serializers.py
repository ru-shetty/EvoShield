from rest_framework import serializers


class MonitoringSerializer(serializers.Serializer):

    total_scans = serializers.IntegerField()
    active_threats = serializers.IntegerField()
    risk_level = serializers.CharField()
    cluster_count = serializers.IntegerField()
    drift_events = serializers.IntegerField()
    rollback_events = serializers.IntegerField()
    history_records = serializers.IntegerField()
    notifications = serializers.ListField(
        child=serializers.CharField()
    )