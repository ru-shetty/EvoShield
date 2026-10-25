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
        "police officer",
        "police department",
        "police station",
        "police ki taraf se",
        "cyber cell",
        "cyber police",
        "police adhikari",
        "पुलिस",
        "साइबर क्राइम",
        "साइबर पुलिस",
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
        "aapko giraftar kiya jayega",
        "aap giraftar hain",
        "giraftar kar lenge",
        "giraftari warrant",
        "jail bhej denge",
        "गिरफ्तार किया जाएगा",
        "गिरफ्तारी वारंट",
        "जेल भेज देंगे",
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
        "abhi turant",
        "phone mat kaato",
        "call mat kaato",
        "फोन मत काटो",
        "कॉल मत काटो",
        "अभी तुरंत",
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
        "paise bhejo",
        "paisa transfer karo",
        "fine jama karo",
        "जुर्माना भरो",
        "पैसे भेजो",
        "पैसा ट्रांसफर करो",
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
        "otp batao",
        "otp bataye",
        "aadhaar number batao",
        "ओटीपी बताओ",
        "आधार नंबर बताओ",
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
        "nakli warrant",
        "fake police notice",
        "नकली वारंट",
        "फर्जी वारंट",
    ],

    "continuous_call_pressure": [
        "do not disconnect",
        "stay on the call",
        "keep the video call on",
        "do not tell anyone",
        "do not contact anyone",
        "stay connected",
        "keep your camera on",
        "kisi ko mat batana",
        "video call par raho",
        "किसी को मत बताना",
        "वीडियो कॉल पर रहो",
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
    "video_call_manipulation": 0.10,
}

VIDEO_CALL_INDICATOR_PATTERNS = [
    "turn your camera on",
    "keep your camera on",
    "do not turn off your camera",
    "stay in front of the camera",
    "show your face on camera",
    "show your id on camera",
    "show your identity card",
    "show your aadhaar on camera",
    "share your screen for verification",
    "show the warrant on screen",
    "video call verification",
    "do not leave the video call",
    "वीडियो कॉल मत काटो",
    "कैमरा चालू रखो",
    "कैमरा बंद मत करो",
    "स्क्रीन शेयर करो",
    "वीडियो कॉल पर रहो",
]


def detect_digital_arrest(text: str, call_type: str | None = None) -> dict:
    """
    Analyze text for digital-arrest and impersonation indicators.

    Parameters
    ----------
    text : str
        Text, OCR output, or speech transcript.
    call_type : str | None
        Optional call context. Video-specific coercion cues are enabled for
        video calls; existing callers can omit this argument.

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

    normalized_call_type = str(call_type or "").strip().lower()
    if normalized_call_type in {"video", "both"}:
        video_matches = [
            pattern for pattern in VIDEO_CALL_INDICATOR_PATTERNS
            if pattern in normalized_text
        ]
        if video_matches:
            detected_indicators["video_call_manipulation"] = video_matches

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
        "call_type": normalized_call_type or None,
    }
    
if __name__ == "__main__":
    sample_text = """
    This is Cyber Crime Police. Your Aadhaar is involved in a criminal case.
    You will be arrested. Do not disconnect this call.
    Send the required payment immediately and provide your OTP.
    """

    result = detect_digital_arrest(sample_text)

    print(result)
