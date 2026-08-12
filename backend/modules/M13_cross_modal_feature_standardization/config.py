# M13_cross_modal_feature_standardization/config.py

"""
Configuration for Module 13:
Cross-Modal Feature Standardization
"""

MODULE_NAME = "Cross-Modal Feature Standardization"

MODULE_VERSION = "1.0.0"

SCHEMA_VERSION = "M13-SCHEMA-v1"

PREPROCESSING_VERSION = "M13-PREPROCESSING-v1"

DEFAULT_MISSING_VALUE = 0.0

SCALER_TYPE = "StandardScaler"

FEATURE_VECTOR_SIZE = 27


# ---------------------------------------------------------
# Common feature schema
# ---------------------------------------------------------

COMMON_FEATURE_SCHEMA = [

    # -------------------------
    # URL
    # -------------------------

    "url_length",
    "url_entropy",
    "suspicious_url_score",
    "domain_age_days",
    "url_risk_score",

    # -------------------------
    # NLP
    # -------------------------

    "nlp_sentiment_score",
    "urgency_score",
    "threat_score",
    "financial_request_score",
    "nlp_risk_score",

    # -------------------------
    # OCR
    # -------------------------

    "ocr_text_length",
    "ocr_suspicious_keyword_score",
    "ocr_threat_score",
    "ocr_risk_score",

    # -------------------------
    # Speech
    # -------------------------

    "speech_duration",
    "speech_threat_score",
    "speech_urgency_score",
    "speech_risk_score",

    # -------------------------
    # Malware
    # -------------------------

    "malware_entropy",
    "malware_behavior_score",
    "malware_anomaly_score",
    "malware_risk_score",

    # -------------------------
    # Digital Arrest
    # -------------------------

    "authority_impersonation_score",
    "video_call_pressure_score",
    "payment_demand_score",
    "legal_threat_score",
    "digital_arrest_risk_score",
]


SCALER_FILE = "m13_scaler.pkl"