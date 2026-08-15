"""
Module 10
Threat Alert Processor
"""


def process_alert_input(data):

    return {
        "risk_level": data.get(
            "risk_level",
            "LOW"
        ),

        "malware_detected": data.get(
            "malware_detected",
            False
        ),

        "phishing_detected": data.get(
            "phishing_detected",
            False
        ),

        "digital_arrest_detected": data.get(
            "digital_arrest_detected",
            False
        ),

        "drift_confirmed": data.get(
            "drift_confirmed",
            False
        )
    }


if __name__ == "__main__":

    sample = {
        "risk_level": "HIGH",
        "malware_detected": True,
        "phishing_detected": False,
        "digital_arrest_detected": True,
        "drift_confirmed": False
    }

    print(process_alert_input(sample))