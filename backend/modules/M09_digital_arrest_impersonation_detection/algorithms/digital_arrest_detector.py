"""
Module 9: Digital Arrest and Impersonation Detection

Detects common digital-arrest and impersonation indicators
from text, OCR text, or speech transcripts.
"""


INDICATOR_PATTERNS = {
    "government_or_police_impersonation": [
        "police",
        "cyber crime",
        "cybercrime",
        "cbi",
        "customs officer",
        "government officer",
        "income tax officer",
        "court officer",
        "supreme court",
        "central bureau of investigation",
    ],

    "threat_language": [
        "you will be arrested",
        "you are under arrest",
        "arrest warrant",
        "arrest you",
        "legal action",
        "criminal case",
        "police case",
        "warrant issued",
        "jail",
        "imprisonment",
    ],

    "urgency": [
        "immediately",
        "urgent",
        "right now",
        "within 10 minutes",
        "within 30 minutes",
        "do it now",
        "act immediately",
        "do not disconnect",
    ],

    "financial_request": [
        "send money",
        "transfer money",
        "pay now",
        "make payment",
        "bank transfer",
        "upi payment",
        "account number",
        "pay the fine",
        "pay the penalty",
    ],

    "otp_pin_aadhaar_pan_request": [
        "otp",
        "one time password",
        "pin",
        "aadhaar",
        "aadhar",
        "pan card",
        "pan number",
        "bank details",
        "debit card",
        "credit card",
    ],

    "fake_document_indicators": [
        "fake warrant",
        "arrest notice",
        "legal notice",
        "court notice",
        "case document",
        "government notice",
        "official document",
        "verification document",
    ],

    "continuous_call_pressure": [
        "do not disconnect",
        "stay on the call",
        "keep the video call on",
        "do not tell anyone",
        "do not contact anyone",
        "stay connected",
        "keep your camera on",
    ],
}


# Weight assigned to each type of indicator.
INDICATOR_WEIGHTS = {
    "government_or_police_impersonation": 0.20,
    "threat_language": 0.20,
    "urgency": 0.10,
    "financial_request": 0.15,
    "otp_pin_aadhaar_pan_request": 0.15,
    "fake_document_indicators": 0.10,
    "continuous_call_pressure": 0.10,
}


def detect_digital_arrest(text: str) -> dict:
    """
    Analyze text for digital-arrest and impersonation indicators.

    Parameters
    ----------
    text : str
        Text, OCR output, or speech transcript.

    Returns
    -------
    dict
        Detection result containing probability, indicators,
        confidence and category.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized_text = " ".join(text.lower().split())

    detected_indicators = {}

    for indicator_type, patterns in INDICATOR_PATTERNS.items():

        matches = []

        for pattern in patterns:
            if pattern in normalized_text:
                matches.append(pattern)

        if matches:
            detected_indicators[indicator_type] = matches

    # Calculate weighted probability.
    probability = sum(
        INDICATOR_WEIGHTS[indicator]
        for indicator in detected_indicators
    )

    probability = min(probability, 1.0)

    # Determine category.
    if probability >= 0.60:
        category = "DIGITAL_ARREST"
    elif probability >= 0.30:
        category = "SUSPICIOUS"
    else:
        category = "NORMAL"

    # Confidence is based on the amount of supporting evidence.
    confidence = min(
        0.50 + (len(detected_indicators) * 0.07),
        0.99
    )

    return {
        "digital_arrest_probability": round(probability, 2),
        "indicators": detected_indicators,
        "confidence": round(confidence, 2),
        "category": category,
    }
    
if __name__ == "__main__":
    sample_text = """
    This is Cyber Crime Police. Your Aadhaar is involved in a criminal case.
    You will be arrested. Do not disconnect this call.
    Send the required payment immediately and provide your OTP.
    """

    result = detect_digital_arrest(sample_text)

    print(result)