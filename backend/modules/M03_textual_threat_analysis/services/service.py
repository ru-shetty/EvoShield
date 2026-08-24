"""
Service layer for M03 - Textual Threat Analysis.
"""

from ..models.models import TextualThreatAnalysis
from ..processors.processor import TextualThreatProcessor


class TextualThreatAnalysisService:
    """
    Service responsible for handling textual threat analysis requests.
    """

    def __init__(self) -> None:
        self.processor = TextualThreatProcessor()

    def analyze_text(self, text: str) -> TextualThreatAnalysis:
        """
        Analyze text through the M03 processing pipeline.
        """

        return self.processor.process(text)

    def analyze_text_to_dict(self, text: str) -> dict:
        """
        Analyze text and return the result as a dictionary.
        """

        analysis = self.analyze_text(text)

        return analysis.to_dict()