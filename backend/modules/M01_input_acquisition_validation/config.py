"""
Configuration for EvoShield Module 1.
"""

from pathlib import Path


# Base directory of this module
BASE_DIR = Path(__file__).resolve().parent


# Supported input types according to the EvoShield specification
SUPPORTED_INPUT_TYPES = {
    "url",
    "text",
    "image",
    "audio",
    "video",
    "file",
}


# Routing destinations
ROUTES = {
    "url": "malicious_url_analysis",
    "text": "textual_threat_analysis",
    "image": "visual_content_ocr_analysis",
    "audio": "speech_media_intelligence",
    "video": "speech_media_intelligence",
    "file": "malware_behavioral_analysis",
}


# Processing states
STATUS_QUEUED = "QUEUED"
STATUS_PROCESSING = "PROCESSING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"


# Maximum text length accepted by the validation layer
MAX_TEXT_LENGTH = 100000


# Maximum URL length accepted by the validation layer
MAX_URL_LENGTH = 2048