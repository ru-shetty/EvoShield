from ..services.service import run_service


def test_module():

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

    result = run_service(sample_input)

    print("\n===== MODULE 12 TEST =====")
    print(result)


if __name__ == "__main__":
    test_module()

def test_module():

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

    result = run_service(sample_input)

    print("\n===== MODULE 12 TEST =====")
    print(result)


if __name__ == "__main__":
    test_module()