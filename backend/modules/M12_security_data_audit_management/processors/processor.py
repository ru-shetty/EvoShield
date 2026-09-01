class SecurityDataProcessor:

    def process(self, raw_data):

        processed_data = {
            "entity_id": raw_data.get("entity_id"),
            "entity_type": raw_data.get("entity_type"),
            "feature_vector": raw_data.get("feature_vector", []),
            "cluster_id": raw_data.get("cluster_id"),
            "trust_level": raw_data.get("trust_level"),
            "status": raw_data.get("status"),
            "risk_history": raw_data.get("risk_history", []),
            "drift_events": raw_data.get("drift_events", []),
            "rollback_logs": raw_data.get("rollback_logs", []),
            "model_name": raw_data.get("model_name"),
            "model_version": raw_data.get("model_version"),
            "analysis_version": raw_data.get("analysis_version")
        }

        return processed_data


if __name__ == "__main__":

    sample_input = {
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

    processor = SecurityDataProcessor()

    result = processor.process(sample_input)

    print(result)