"""
Configuration for M02 - Malicious URL Analysis.

This module contains configurable thresholds and constants
used by the malicious URL detection pipeline.
"""

MODULE_NAME = "M02_MALICIOUS_URL_ANALYSIS"
MODULE_VERSION = "1.0.0"

# URL analysis thresholds
SUSPICIOUS_URL_SCORE_THRESHOLD = 0.50
MALICIOUS_URL_SCORE_THRESHOLD = 0.75

# URL length thresholds
MAX_SAFE_URL_LENGTH = 2048
SUSPICIOUS_URL_LENGTH = 150

# Suspicious URL indicators
SUSPICIOUS_SCHEMES = {
    "javascript",
    "data",
    "file",
}

SUSPICIOUS_EXTENSIONS = {
    ".exe",
    ".scr",
    ".bat",
    ".cmd",
    ".js",
    ".vbs",
    ".ps1",
}

# Suspicious URL keywords frequently associated with phishing
SUSPICIOUS_KEYWORDS = {
    "login",
    "verify",
    "verification",
    "account",
    "secure",
    "security",
    "update",
    "confirm",
    "password",
    "signin",
    "bank",
    "payment",
    "wallet",
    "credential",
}

# Feature weights used by the URL analysis algorithm
FEATURE_WEIGHTS = {
    "https": 0.10,
    "ip_address": 0.20,
    "url_length": 0.15,
    "suspicious_keyword": 0.15,
    "special_character": 0.10,
    "suspicious_extension": 0.15,
    "suspicious_scheme": 0.15,
}

# Risk labels
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

# Analysis status
STATUS_SAFE = "SAFE"
STATUS_SUSPICIOUS = "SUSPICIOUS"
STATUS_MALICIOUS = "MALICIOUS"