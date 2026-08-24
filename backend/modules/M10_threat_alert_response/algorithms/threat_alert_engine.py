"""
Module 10
Threat Alert & Response Recommendation Engine
"""


def generate_alerts(
    risk_level="LOW",
    malware_detected=False,
    phishing_detected=False,
    digital_arrest_detected=False,
    drift_confirmed=False
):
    alerts = []

    # High Risk Alert
    if risk_level in ["HIGH", "CRITICAL"]:
        alerts.append({
            "alert_type": "HIGH_RISK",
            "priority": "HIGH",
            "reason": f"Risk level is {risk_level}",
            "recommended_action":
                "Investigate immediately and monitor activity."
        })

    # Malware Alert
    if malware_detected:
        alerts.append({
            "alert_type": "MALWARE",
            "priority": "HIGH",
            "reason": "Malware behavior detected",
            "recommended_action":
                "Run antivirus scan and isolate affected system."
        })

    # Phishing Alert
    if phishing_detected:
        alerts.append({
            "alert_type": "PHISHING",
            "priority": "HIGH",
            "reason": "Phishing indicators found",
            "recommended_action":
                "Block sender and avoid clicking suspicious links."
        })

    # Digital Arrest Alert
    if digital_arrest_detected:
        alerts.append({
            "alert_type": "DIGITAL_ARREST",
            "priority": "CRITICAL",
            "reason": "Digital arrest scam indicators detected",
            "recommended_action":
                "Do not share OTP, Aadhaar, PAN or bank details."
        })

    # Drift / Rollback Alert
    if drift_confirmed:
        alerts.append({
            "alert_type": "DRIFT_ROLLBACK",
            "priority": "MEDIUM",
            "reason": "Concept drift detected",
            "recommended_action":
                "Review model performance and rollback if needed."
        })

    return {
        "total_alerts": len(alerts),
        "notification_required": len(alerts) > 0,
        "alerts": alerts
    }


if __name__ == "__main__":

    result = generate_alerts(
        risk_level="CRITICAL",
        malware_detected=True,
        phishing_detected=True,
        digital_arrest_detected=True,
        drift_confirmed=True
    )

    print(result)