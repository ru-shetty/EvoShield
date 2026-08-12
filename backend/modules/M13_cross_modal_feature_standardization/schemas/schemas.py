# M13_cross_modal_feature_standardization/schema.py

COMMON_SCHEMA = [
    # URL features
    "url_length",
    "url_entropy",
    "suspicious_url_score",
    "domain_age_days",
    "url_risk_score",

    # NLP features
    "nlp_sentiment_score",
    "urgency_score",
    "threat_score",
    "financial_request_score",
    "nlp_risk_score",

    # OCR features
    "ocr_text_length",
    "ocr_suspicious_keyword_score",
    "ocr_threat_score",
    "ocr_risk_score",

    # Speech features
    "speech_duration",
    "speech_threat_score",
    "speech_urgency_score",
    "speech_risk_score",

    # Malware features
    "malware_entropy",
    "malware_behavior_score",
    "malware_anomaly_score",
    "malware_risk_score",

    # Digital-arrest features
    "authority_impersonation_score",
    "video_call_pressure_score",
    "payment_demand_score",
    "legal_threat_score",
    "digital_arrest_risk_score",
]

FEATURE_VECTOR_SIZE = len(COMMON_SCHEMA)