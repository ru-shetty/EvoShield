"""
Module 9: Input Processor

Prepares text, OCR output, or speech transcripts
for digital-arrest detection.
"""

import re

from ..algorithms.digital_arrest_detector import detect_digital_arrest


def normalize_text(text: str) -> str:
    """
    Clean and normalize incoming text.

    Parameters
    ----------
    text : str
        Text, OCR output, or speech transcript.

    Returns
    -------
    str
        Normalized text.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # Convert to lowercase
    text = text.lower()

    # Replace multiple spaces/newlines with one space
    text = re.sub(r"\s+", " ", text)

    # Remove unnecessary special characters,
    # while keeping useful punctuation.
    text = re.sub(r"[^\w\s.,!?@:/-]", "", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text


def process_input(text: str) -> dict:
    """
    Process incoming evidence and run digital-arrest detection.
    """

    normalized_text = normalize_text(text)

    detection_result = detect_digital_arrest(normalized_text)

    return {
        "original_text": text,
        "normalized_text": normalized_text,
        "character_count": len(normalized_text),
        "word_count": len(normalized_text.split()),
        "detection": detection_result,
    }


if __name__ == "__main__":

    sample_text = """
    THIS IS CYBER CRIME POLICE!!!
    Your Aadhaar is involved in a criminal case.
    DO NOT DISCONNECT THE CALL!!!
    """

    result = process_input(sample_text)

    print(result)