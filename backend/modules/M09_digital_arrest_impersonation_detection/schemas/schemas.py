"""
Module 9: Digital Arrest & Impersonation Detection Schemas
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DetectionResult:
    """
    Standardized digital-arrest detection result.
    """

    digital_arrest_probability: float
    indicators: Dict[str, List[str]]
    confidence: float
    category: str


@dataclass
class AnalysisResponse:
    """
    Standardized response returned by Module 9.
    """

    module: str
    input_type: str
    result: DetectionResult
    character_count: int
    word_count: int