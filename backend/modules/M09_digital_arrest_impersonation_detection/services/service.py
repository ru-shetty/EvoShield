"""
Module 9: Digital Arrest & Impersonation Detection Service

Coordinates input processing and digital-arrest detection.
"""

from ..processors.processor import process_input


def analyze_evidence(text: str) -> dict:
    """
    Analyze text evidence for digital-arrest or impersonation indicators.

    The input is first normalized by the processor and then
    passed through the detection algorithm.
    """

    if not text or not text.strip():
        raise ValueError("Evidence text cannot be empty.")

    result = process_input(text)

    return {
        "module": "M09",
        "input_type": "text",
        "result": result["detection"],
        "metadata": {
            "character_count": result["character_count"],
            "word_count": result["word_count"],
        },
    }


if __name__ == "__main__":

    sample_text = """
    This is Cyber Crime Police.
    Your Aadhaar is involved in a criminal case.
    You will be arrested.
    Do not disconnect the call.
    Send the payment immediately and provide your OTP.
    """

    result = analyze_evidence(sample_text)

    print(result)