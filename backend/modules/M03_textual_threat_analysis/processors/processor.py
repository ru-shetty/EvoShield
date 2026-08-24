"""
Processor for M03 - Textual Threat Analysis.
"""

from typing import Any
from uuid import uuid4

from ..algorithms.text_analyzer import TextualThreatAnalyzer
from ..models.models import TextualThreatAnalysis


class TextualThreatProcessor:
    """
    Coordinates text input with the textual threat analysis algorithm.
    """

    def __init__(self) -> None:
        self.analyzer = TextualThreatAnalyzer()

    def process(self, text: str) -> TextualThreatAnalysis:
        """
        Analyze text and return a TextualThreatAnalysis model.
        """

        entity_id = self._generate_entity_id()

        result = self.analyzer.analyze(text)

        analysis = TextualThreatAnalysis(
            entity_id=entity_id,
            text=text,
            score=result["score"],
            status=result["status"],
            risk_level=result["risk_level"],
            indicators=result["indicators"],
            features=result["features"],
        )

        return analysis

    @staticmethod
    def _generate_entity_id() -> str:
        """
        Generate a unique entity identifier.
        """

        return f"TEXT-{uuid4().hex}"

    def process_to_dict(self, text: str) -> dict[str, Any]:
        """
        Analyze text and directly return a dictionary result.
        """

        analysis = self.process(text)

        return analysis.to_dict()