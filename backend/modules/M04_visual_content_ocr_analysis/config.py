"""
Configuration for M04 - Visual Content OCR Analysis.

This module contains configuration values used by the
visual content and OCR analysis pipeline.
"""

MODULE_NAME = "M04_VISUAL_CONTENT_OCR_ANALYSIS"
MODULE_VERSION = "1.0.0"

# OCR configuration
DEFAULT_LANGUAGE = "eng"
OCR_CONFIDENCE_THRESHOLD = 0.60

# Image validation
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100
MAX_IMAGE_WIDTH = 10000
MAX_IMAGE_HEIGHT = 10000

# Suspicious text thresholds
SUSPICIOUS_TEXT_LENGTH = 500
HIGH_RISK_TEXT_LENGTH = 2000

# Suspicious visual/text indicators
SUSPICIOUS_KEYWORDS = {
    "urgent",
    "verify",
    "verification",
    "password",
    "credential",
    "login",
    "signin",
    "account",
    "security",
    "payment",
    "bank",
    "transfer",
    "refund",
    "invoice",
    "confirm",
    "suspended",
    "blocked",
    "warning",
    "alert",
    "click",
    "download",
}

# Suspicious phrases commonly found in malicious visual content
SUSPICIOUS_PHRASES = {
    "verify your account",
    "confirm your identity",
    "account has been suspended",
    "your account will be closed",
    "enter your password",
    "provide your credentials",
    "make a payment",
    "send money",
    "click the link",
    "download the attachment",
}

# Feature weights
FEATURE_WEIGHTS = {
    "suspicious_keyword": 0.20,
    "suspicious_phrase": 0.25,
    "high_text_density": 0.10,
    "low_ocr_confidence": 0.10,
    "financial_content": 0.15,
    "credential_content": 0.20,
}

# Risk thresholds
SUSPICIOUS_SCORE_THRESHOLD = 0.40
MALICIOUS_SCORE_THRESHOLD = 0.70

# Risk labels
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

# Analysis status
STATUS_SAFE = "SAFE"
STATUS_SUSPICIOUS = "SUSPICIOUS"
STATUS_MALICIOUS = "MALICIOUS"