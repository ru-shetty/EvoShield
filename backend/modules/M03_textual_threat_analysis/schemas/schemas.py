"""
Schemas for M03 - Textual Threat Analysis.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TextAnalysisRequest:
    """
    Input schema for textual threat analysis.
    """

    text: str


@dataclass
class TextAnalysisResponse:
    """
    Output schema for textual threat analysis.
    """

    entity_id: str
    text: str
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
            "score": self.score,
            "status": self.status,
            "risk_level": self.risk_level,
            "indicators": self.indicators,
            "features": self.features,
        }