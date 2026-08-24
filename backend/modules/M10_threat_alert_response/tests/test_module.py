"""
Module 10 Complete End-to-End Test
"""

from backend.modules.M10_threat_alert_response.services.service import (
    create_alert_response
)


def test_module():

    sample_data = {
        "risk_level": "CRITICAL",
        "malware_detected": True,
        "phishing_detected": True,
        "digital_arrest_detected": True,
        "drift_confirmed": True
    }

    result = create_alert_response(sample_data)

    print("\n===== MODULE 10 TEST =====")
    print(result)

    return result


if __name__ == "__main__":
    test_module()