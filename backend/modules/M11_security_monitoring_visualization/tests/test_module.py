from backend.modules.M11_security_monitoring_visualization.services.service import (
    run_service,
)


def test_module():

    sample_input = {
        "total_scans": 100,
        "active_threats": 4,
        "risk_level": "HIGH",
        "cluster_count": 2,
        "drift_events": 1,
        "rollback_events": 0,
        "history_records": 200,
        "notifications": [
            "Threat detected",
            "Risk increased",
        ],
    }

    result = run_service(sample_input)

    print("\n===== MODULE 11 TEST =====")
    print(result)


if __name__ == "__main__":
    test_module()