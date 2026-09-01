from datetime import datetime


class SecurityDataAuditEngine:

    def store_security_record(self, data):

        record = {
            "entity": {
                "entity_id": data.get("entity_id"),
                "entity_type": data.get("entity_type")
            },
            "features": {
                "feature_vector": data.get("feature_vector", [])
            },
            "cluster": {
                "cluster_id": data.get("cluster_id")
            },
            "trust": {
                "trust_level": data.get("trust_level"),
                "status": data.get("status")
            },
            "history": {
                "risk_history": data.get("risk_history", [])
            },
            "drift": data.get("drift_events", []),
            "rollback": data.get("rollback_logs", []),
            "model_metadata": {
                "model_name": data.get("model_name"),
                "model_version": data.get("model_version"),
                "analysis_version": data.get("analysis_version")
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return record


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

    engine = SecurityDataAuditEngine()

    result = engine.store_security_record(sample_data)

    print(result)