"""Desktop alerts for scan results that cross the existing risk thresholds."""
import logging
import os
from urllib.parse import urlsplit


logger = logging.getLogger(__name__)
ALERT_VERDICTS = {"HIGH", "MEDIUM", "REVIEW"}


def _risk_label(verdict):
    return {
        "HIGH": "High risk",
        "MEDIUM": "Suspicious",
        "REVIEW": "Needs review",
    }.get(verdict, "")


def _entity_label(record):
    call = record.details.get("call_details", {}) if isinstance(record.details, dict) else {}
    call_type = call.get("call_type")
    if record.source in {"windows-live-call", "android-call"} or call:
        return {
            "video": "video call",
            "both": "voice/video call",
            "voice": "voice call",
        }.get(call_type, "call")
    return {
        "url": "website",
        "file": "file",
        "image": "image",
        "text": "message",
    }.get(record.entity_type, "security check")


def _summary(record):
    details = record.details if isinstance(record.details, dict) else {}
    if record.entity_type == "url":
        analysis = details.get("url_analysis", {})
        indicators = analysis.get("indicators", [])
        names = {
            "brand_lookalike": "possible brand lookalike",
            "suspicious_keyword_in_host": "suspicious words in the website name",
            "ip_address": "numeric website address",
            "punycode_host": "encoded website name",
            "url_userinfo": "misleading sign-in information in the address",
            "suspicious_extension": "risky download type",
            "non_https": "no HTTPS connection",
        }
        reasons = [names[item] for item in indicators if item in names]
        if reasons:
            return "Warning signs: " + ", ".join(reasons[:3]) + ". Avoid entering passwords, codes, or payment details."
        return "This website address was flagged by EvoShield. Avoid entering sensitive information until verified."

    if record.entity_type == "file":
        file_info = details.get("static_file_analysis", {})
        if file_info.get("eicar_test_signature"):
            return "The harmless EICAR test pattern was found in this file."
        return "This file needs review. Do not open it unless you trust the source."

    if record.entity_type == "image":
        analysis = details.get("image_ocr_analysis", {})
        names = {
            "suspicious_keyword": "suspicious words in the image",
            "suspicious_phrase": "possible phishing instructions in the image",
            "financial_content": "payment or money-related wording",
            "credential_content": "password or account-verification wording",
            "high_text_density": "a large amount of text",
        }
        reasons = [names[item] for item in analysis.get("indicators", []) if item in names]
        reasons.extend(str(item).replace("_", " ") for item in analysis.get("text_indicators", [])[:2])
        if analysis.get("digital_arrest_category") == "DIGITAL_ARREST":
            reasons.append("possible digital-arrest scam wording")
        if reasons:
            return "Warning signs: " + ", ".join(reasons[:3]) + ". Do not follow links or share passwords, codes, or payment details."
        return "Text in this image was flagged as suspicious. Do not follow its instructions until verified."

    arrest = details.get("digital_arrest", {})
    groups = arrest.get("indicators", {})
    if isinstance(groups, dict):
        indicator_names = list(groups)
    elif isinstance(groups, list):
        indicator_names = groups
    else:
        indicator_names = []
    if indicator_names:
        readable = ", ".join(str(item).replace("_", " ") for item in indicator_names[:3])
        return f"Warning signs: {readable}. Do not pay or share one-time codes under pressure."
    return "EvoShield found suspicious language. Verify the sender through a trusted contact."


def _subject(record):
    if record.entity_type == "url":
        try:
            return urlsplit(record.subject).hostname or "Website address"
        except ValueError:
            return "Website address"
    return (record.subject or "New threat alert").strip()[:90]


def notify_scan_result(record):
    """Show a Windows toast for every non-low scan result, if available."""
    # The Windows call monitor already raises its own toast before submitting
    # the alert, so avoid showing that same call warning twice.
    if record.verdict not in ALERT_VERDICTS or record.source == "windows-live-call" or os.name != "nt":
        return
    try:
        from winotify import Notification

        title = f"EvoShield: {_risk_label(record.verdict)} {_entity_label(record)}"
        subject = _subject(record)
        message = f"{subject}. {_summary(record)}"
        Notification(app_id="EvoShield", title=title[:64], msg=message[:240], duration="long").show()
    except Exception:
        # A notification failure must never fail or discard the security scan.
        logger.exception("Could not display the EvoShield desktop threat notification")
