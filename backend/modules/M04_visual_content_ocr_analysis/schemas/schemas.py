"""
Schemas for M04 - Visual Content OCR Analysis.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OCRAnalysisRequest:
    """
    Input schema for visual content OCR analysis.
    """

    text: str
    ocr_confidence: float = 1.0


@dataclass
class OCRAnalysisResponse:
    """
    Output schema for visual content OCR analysis.
    """

    entity_id: str
    text: str
    ocr_confidence: float
    score: float
    status: str
    risk_level: str

    indicators: list[str] = field(default_factory=list)
    features: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the response schema into a dictionary.
        """

        return {
            "entity_id": self.entity_id,
            "text": self.text,
            "ocr_confidence": self.ocr_confidence,
            "score": self.score,
            "status": self.status,
            "risk_level": self.risk_level,
            "indicators": self.indicators,
            "features": self.features,
        }