from ..processors.processor import process_alert_input
from ..algorithms.threat_alert_engine import generate_alerts


def create_alert_response(data):

    processed_data = process_alert_input(data)

    result = generate_alerts(
        risk_level=processed_data["risk_level"],
        malware_detected=processed_data["malware_detected"],
        phishing_detected=processed_data["phishing_detected"],
        digital_arrest_detected=processed_data[
            "digital_arrest_detected"
        ],
        drift_confirmed=processed_data[
            "drift_confirmed"
        ]
    )

    return {
        "module": "M10",
        "input_type": "threat_analysis",
        "result": result
    }


if __name__ == "__main__":

    sample = {
        "risk_level": "CRITICAL",
        "malware_detected": True,
        "phishing_detected": True,
        "digital_arrest_detected": True,
        "drift_confirmed": True
    }

    print(create_alert_response(sample))