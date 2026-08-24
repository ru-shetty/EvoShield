"""
Service layer for M04 - Visual Content OCR Analysis.
"""

from ..models.models import VisualContentOCRAnalysis
from ..processors.processor import VisualContentOCRProcessor


class VisualContentOCRAnalysisService:
    """
    Service responsible for handling visual content OCR analysis.
    """

    def __init__(self) -> None:
        self.processor = VisualContentOCRProcessor()

    def analyze_text(
        self,
        text: str,
        ocr_confidence: float = 1.0,
    ) -> VisualContentOCRAnalysis:
        """
        Analyze OCR text through the M04 processing pipeline.
        """

        return self.processor.process(
            text=text,
            ocr_confidence=ocr_confidence,
        )

    def analyze_text_to_dict(
        self,
        text: str,
        ocr_confidence: float = 1.0,
    ) -> dict:
        """
        Analyze OCR text and return the result as a dictionary.
        """

        analysis = self.analyze_text(
            text=text,
            ocr_confidence=ocr_confidence,
        )

        return analysis.to_dict()