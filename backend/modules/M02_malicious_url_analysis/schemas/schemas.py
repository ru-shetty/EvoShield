"""
Schemas for M02 - Malicious URL Analysis.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class URLAnalysisRequest:
    """
    Input schema for malicious URL analysis.
    """

    url: str


@dataclass
class URLAnalysisResponse:
    """
    Output schema for malicious URL analysis.
    """

    entity_id: str
    url: str
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
            "url": self.url,
            "score": self.score,
            "status": self.status,
            "risk_level": self.risk_level,
            "indicators": self.indicators,
            "features": self.features,
        }