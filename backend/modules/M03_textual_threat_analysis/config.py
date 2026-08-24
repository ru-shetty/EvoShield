"""
Configuration for M03 - Textual Threat Analysis.

This module contains configuration values used by the
textual threat detection pipeline.
"""

MODULE_NAME = "M03_TEXTUAL_THREAT_ANALYSIS"
MODULE_VERSION = "1.0.0"

# Risk score thresholds
SUSPICIOUS_TEXT_SCORE_THRESHOLD = 0.40
MALICIOUS_TEXT_SCORE_THRESHOLD = 0.70

# Text length thresholds
MIN_TEXT_LENGTH = 1
SUSPICIOUS_TEXT_LENGTH = 5000

# Suspicious textual indicators
SUSPICIOUS_KEYWORDS = {
    "urgent",
    "immediately",
    "verify",
    "verification",
    "account",
    "password",
    "credential",
    "login",
    "signin",
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
    "attachment",
}

# Threat-related phrases
THREAT_PHRASES = {
    "your account will be closed",
    "account has been suspended",
    "verify your account",
    "confirm your identity",
    "send money",
    "make a payment",
    "click the link",
    "download the attachment",
    "provide your password",
    "provide your credentials",
}

# Social engineering indicators
SOCIAL_ENGINEERING_INDICATORS = {
    "urgency",
    "fear",
    "authority",
    "financial_request",
    "credential_request",
}

# Feature weights
FEATURE_WEIGHTS = {
    "suspicious_keyword": 0.20,
    "threat_phrase": 0.25,
    "urgency_indicator": 0.15,
    "credential_request": 0.15,
    "financial_request": 0.15,
    "excessive_special_characters": 0.10,
}

# Risk labels
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

# Analysis status
STATUS_SAFE = "SAFE"
STATUS_SUSPICIOUS = "SUSPICIOUS"
STATUS_MALICIOUS = "MALICIOUS"