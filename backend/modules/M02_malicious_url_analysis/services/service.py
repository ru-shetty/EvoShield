"""
Service layer for M02 - Malicious URL Analysis.
"""

from ..models.models import MaliciousURLAnalysis
from ..processors.processor import MaliciousURLProcessor


class MaliciousURLAnalysisService:
    """
    Service responsible for handling malicious URL analysis requests.
    """

    def __init__(self) -> None:
        self.processor = MaliciousURLProcessor()

    def analyze_url(self, url: str) -> MaliciousURLAnalysis:
        """
        Analyze a URL through the M02 processing pipeline.
        """

        return self.processor.process(url)

    def analyze_url_to_dict(self, url: str) -> dict:
        """
        Analyze a URL and return the result as a dictionary.
        """

        analysis = self.analyze_url(url)

        return analysis.to_dict()