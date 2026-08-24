"""
Processor for M02 - Malicious URL Analysis.
"""

from typing import Any
from uuid import uuid4

from ..algorithms.url_analyzer import MaliciousURLAnalyzer
from ..models.models import MaliciousURLAnalysis


class MaliciousURLProcessor:
    """
    Coordinates URL input with the malicious URL analysis algorithm.
    """

    def __init__(self) -> None:
        self.analyzer = MaliciousURLAnalyzer()

    def process(self, url: str) -> MaliciousURLAnalysis:
        """
        Analyze a URL and return a MaliciousURLAnalysis model.
        """

        entity_id = self._generate_entity_id()

        result = self.analyzer.analyze(url)

        analysis = MaliciousURLAnalysis(
            entity_id=entity_id,
            url=url,
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

        return f"URL-{uuid4().hex}"

    def process_to_dict(self, url: str) -> dict[str, Any]:
        """
        Analyze a URL and directly return a dictionary result.
        """

        analysis = self.process(url)

        return analysis.to_dict()