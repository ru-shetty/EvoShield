"""
Processor for M04 - Visual Content OCR Analysis.
"""

from typing import Any
from uuid import uuid4

from ..algorithms.ocr_analyzer import VisualContentOCRAnalyzer
from ..models.models import VisualContentOCRAnalysis


class VisualContentOCRProcessor:
    """
    Coordinates OCR text input with the visual content
    threat analysis algorithm.
    """

    def __init__(self) -> None:
        self.analyzer = VisualContentOCRAnalyzer()

    def process(
        self,
        text: str,
        ocr_confidence: float = 1.0,
    ) -> VisualContentOCRAnalysis:
        """
        Analyze OCR text and return a VisualContentOCRAnalysis model.
        """

        entity_id = self._generate_entity_id()

        result = self.analyzer.analyze(
            text=text,
            ocr_confidence=ocr_confidence,
        )

        analysis = VisualContentOCRAnalysis(
            entity_id=entity_id,
            text=text,
            ocr_confidence=result["ocr_confidence"],
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

        return f"OCR-{uuid4().hex}"

    def process_to_dict(
        self,
        text: str,
        ocr_confidence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Analyze OCR text and directly return a dictionary result.
        """

        analysis = self.process(
            text=text,
            ocr_confidence=ocr_confidence,
        )

        return analysis.to_dict()