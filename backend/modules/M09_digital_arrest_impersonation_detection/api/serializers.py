"""
Module 9 API serializers.
"""

from dataclasses import dataclass


@dataclass
class DigitalArrestRequest:
    """
    Request data for digital-arrest analysis.
    """

    text: str

    @classmethod
    def from_dict(cls, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")

        text = data.get("text")

        if not isinstance(text, str):
            raise ValueError("'text' must be a string.")

        if not text.strip():
            raise ValueError("'text' cannot be empty.")

        return cls(text=text)