class MonitoringSchema:

    required_fields = [
        "total_scans",
        "active_threats",
        "risk_level",
        "cluster_count",
        "drift_events",
        "rollback_events",
        "history_records",
        "notifications"
    ]

    @classmethod
    def validate(cls, data):

        missing_fields = []

        for field in cls.required_fields:
            if field not in data:
                missing_fields.append(field)

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields
        }


if __name__ == "__main__":

    sample_data = {
        "total_scans": 100,
        "active_threats": 4,
        "risk_level": "HIGH",
        "cluster_count": 2,
        "drift_events": 1,
        "rollback_events": 0,
        "history_records": 200,
        "notifications": []
    }

    print(MonitoringSchema.validate(sample_data))