"""
Data models for M04 - Visual Content OCR Analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class VisualContentOCRAnalysis:
    """
    Represents the result of visual content OCR analysis.
    """

    entity_id: str
    text: str

    ocr_confidence: float = 1.0
    score: float = 0.0
    status: str = "SAFE"
    risk_level: str = "LOW"

    indicators: list[str] = field(default_factory=list)
    features: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_result(
        self,
        ocr_confidence: float,
        score: float,
        status: str,
        risk_level: str,
        indicators: list[str] | None = None,
        features: dict[str, Any] | None = None,
    ) -> None:
        """
        Update the OCR analysis result.
        """

        self.ocr_confidence = ocr_confidence
        self.score = score
        self.status = status
        self.risk_level = risk_level

        if indicators is not None:
            self.indicators = indicators

        if features is not None:
            self.features = features

        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }