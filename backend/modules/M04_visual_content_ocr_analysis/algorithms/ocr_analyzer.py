"""
Visual content OCR analysis algorithm for M04.
"""

import re
from typing import Any

from ..config import (
    FEATURE_WEIGHTS,
    MALICIOUS_SCORE_THRESHOLD,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    STATUS_MALICIOUS,
    STATUS_SAFE,
    STATUS_SUSPICIOUS,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_PHRASES,
    SUSPICIOUS_SCORE_THRESHOLD,
)


class VisualContentOCRAnalyzer:
    """
    Analyzes OCR-extracted text from visual content and identifies
    suspicious or potentially malicious characteristics.
    """

    def analyze(
        self,
        text: str,
        ocr_confidence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Analyze OCR text and return a threat assessment.
        """

        if not isinstance(text, str) or not text.strip():
            return self._result(
                text=text,
                ocr_confidence=ocr_confidence,
                score=1.0,
                status=STATUS_MALICIOUS,
                risk=RISK_HIGH,
                indicators=["empty_or_invalid_text"],
                features={},
            )

        normalized_text = text.lower().strip()

        features = {
            "suspicious_keyword": self._check_keywords(
                normalized_text
            ),
            "suspicious_phrase": self._check_phrases(
                normalized_text
            ),
            "high_text_density": self._check_text_density(
                normalized_text
            ),
            "low_ocr_confidence": self._check_ocr_confidence(
                ocr_confidence
            ),
            "financial_content": self._check_financial_content(
                normalized_text
            ),
            "credential_content": self._check_credential_content(
                normalized_text
            ),
        }

        indicators = [
            feature_name
            for feature_name, detected in features.items()
            if detected
        ]

        score = self._calculate_score(features)

        if score >= MALICIOUS_SCORE_THRESHOLD:
            status = STATUS_MALICIOUS
            risk = RISK_HIGH
        elif score >= SUSPICIOUS_SCORE_THRESHOLD:
            status = STATUS_SUSPICIOUS
            risk = RISK_MEDIUM
        else:
            status = STATUS_SAFE
            risk = RISK_LOW

        return self._result(
            text=text,
            ocr_confidence=ocr_confidence,
            score=score,
            status=status,
            risk=risk,
            indicators=indicators,
            features=features,
        )

    @staticmethod
    def _check_keywords(text: str) -> bool:
        """
        Detect suspicious keywords in OCR text.
        """

        return any(
            keyword in text
            for keyword in SUSPICIOUS_KEYWORDS
        )

    @staticmethod
    def _check_phrases(text: str) -> bool:
        """
        Detect suspicious phrases in OCR text.
        """

        return any(
            phrase in text
            for phrase in SUSPICIOUS_PHRASES
        )

    @staticmethod
    def _check_text_density(text: str) -> bool:
        """
        Detect unusually long OCR text content.
        """

        return len(text) > 500

    @staticmethod
    def _check_ocr_confidence(
        ocr_confidence: float,
    ) -> bool:
        """
        Detect low OCR confidence.
        """

        return ocr_confidence < 0.60

    @staticmethod
    def _check_financial_content(text: str) -> bool:
        """
        Detect financial-related content.
        """

        financial_patterns = [
            r"\bbank\b",
            r"\bpayment\b",
            r"\bpay\b",
            r"\btransfer\b",
            r"\bmoney\b",
            r"\brefund\b",
            r"\binvoice\b",
            r"\bcredit\s+card\b",
            r"\bdebit\s+card\b",
            r"\baccount\s+number\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in financial_patterns
        )

    @staticmethod
    def _check_credential_content(text: str) -> bool:
        """
        Detect credential or authentication-related content.
        """

        credential_patterns = [
            r"\bpassword\b",
            r"\bcredential(s)?\b",
            r"\blogin\b",
            r"\bsign\s*in\b",
            r"\busername\b",
            r"\bverification\s+code\b",
            r"\botp\b",
            r"\bpin\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in credential_patterns
        )

    @staticmethod
    def _calculate_score(
        features: dict[str, bool],
    ) -> float:
        """
        Calculate the weighted threat score.
        """

        score = 0.0

        for feature_name, detected in features.items():
            if detected:
                score += FEATURE_WEIGHTS.get(
                    feature_name,
                    0.0,
                )

        return round(
            min(score, 1.0),
            4,
        )

    @staticmethod
    def _result(
        text: str,
        ocr_confidence: float,
        score: float,
        status: str,
        risk: str,
        indicators: list[str],
        features: dict[str, bool],
    ) -> dict[str, Any]:
        """
        Create a standardized OCR analysis result.
        """

        return {
            "text": text,
            "ocr_confidence": ocr_confidence,
            "score": score,
            "status": status,
            "risk_level": risk,
            "indicators": indicators,
            "features": features,
        }