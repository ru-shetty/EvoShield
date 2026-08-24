"""
Module 10 Serializer
"""


def validate_alert_request(data):

    if "risk_level" not in data:
        raise ValueError(
            "risk_level is required"
        )

    return data