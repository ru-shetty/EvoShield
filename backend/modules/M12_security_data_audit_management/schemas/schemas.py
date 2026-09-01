class SecurityAuditSchema:

    required_fields = [
        "entity_id",
        "entity_type",
        "feature_vector",
        "cluster_id",
        "trust_level",
        "status",
        "risk_history",
        "drift_events",
        "rollback_logs",
        "model_name",
        "model_version",
        "analysis_version"
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
        "entity_id": "ENT001",
        "entity_type": "URL",
        "feature_vector": [0.3, 0.5, 0.8],
        "cluster_id": 2,
        "trust_level": 85,
        "status": "SAFE",
        "risk_history": [20, 25, 15],
        "drift_events": [],
        "rollback_logs": [],
        "model_name": "EvoShield",
        "model_version": "1.0",
        "analysis_version": "12.0"
    }

    print(SecurityAuditSchema.validate(sample_data))