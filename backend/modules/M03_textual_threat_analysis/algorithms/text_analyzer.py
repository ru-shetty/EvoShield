"""
Textual threat analysis algorithm for M03.
"""

import re

from ..config import (
    FEATURE_WEIGHTS,
    MALICIOUS_TEXT_SCORE_THRESHOLD,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    STATUS_MALICIOUS,
    STATUS_SAFE,
    STATUS_SUSPICIOUS,
    SUSPICIOUS_KEYWORDS,
    THREAT_PHRASES,
)


class TextualThreatAnalyzer:
    """
    Analyzes textual content for suspicious and malicious
    threat indicators.
    """

    def analyze(self, text: str) -> dict:
        """
        Analyze text and return a threat assessment.
        """

        if not isinstance(text, str) or not text.strip():
            return self._result(
                text=text,
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
            "threat_phrase": self._check_threat_phrases(
                normalized_text
            ),
            "urgency_indicator": self._check_urgency(
                normalized_text
            ),
            "credential_request": self._check_credential_request(
                normalized_text
            ),
            "financial_request": self._check_financial_request(
                normalized_text
            ),
            "excessive_special_characters": (
                self._check_special_characters(normalized_text)
            ),
        }

        indicators = [
            feature_name
            for feature_name, detected in features.items()
            if detected
        ]

        score = self._calculate_score(features)

        if score >= MALICIOUS_TEXT_SCORE_THRESHOLD:
            status = STATUS_MALICIOUS
            risk = RISK_HIGH
        elif score >= 0.40:
            status = STATUS_SUSPICIOUS
            risk = RISK_MEDIUM
        else:
            status = STATUS_SAFE
            risk = RISK_LOW

        return self._result(
            text=text,
            score=score,
            status=status,
            risk=risk,
            indicators=indicators,
            features=features,
        )

    @staticmethod
    def _check_keywords(text: str) -> bool:
        """
        Detect suspicious keywords in the text.
        """

        return any(
            keyword in text
            for keyword in SUSPICIOUS_KEYWORDS
        )

    @staticmethod
    def _check_threat_phrases(text: str) -> bool:
        """
        Detect known threat-related phrases.
        """

        return any(
            phrase in text
            for phrase in THREAT_PHRASES
        )

    @staticmethod
    def _check_urgency(text: str) -> bool:
        """
        Detect urgency-related language.
        """

        urgency_words = {
            "urgent",
            "immediately",
            "now",
            "asap",
            "within 24 hours",
            "within 1 hour",
            "last chance",
            "act now",
        }

        return any(
            word in text
            for word in urgency_words
        )

    @staticmethod
    def _check_credential_request(text: str) -> bool:
        """
        Detect requests for credentials or authentication data.
        """

        credential_patterns = [
            r"\benter\s+(your\s+)?password\b",
            r"\bprovide\s+(your\s+)?password\b",
            r"\bshare\s+(your\s+)?password\b",
            r"\benter\s+(your\s+)?credentials\b",
            r"\bprovide\s+(your\s+)?credentials\b",
            r"\bsend\s+(your\s+)?credentials\b",
            r"\bconfirm\s+(your\s+)?login\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in credential_patterns
        )

    @staticmethod
    def _check_financial_request(text: str) -> bool:
        """
        Detect requests involving money or financial transactions.
        """

        financial_patterns = [
            r"\bsend\s+money\b",
            r"\bmake\s+a\s+payment\b",
            r"\btransfer\s+money\b",
            r"\bsend\s+payment\b",
            r"\bpay\s+now\b",
            r"\bbank\s+account\b",
            r"\bcredit\s+card\b",
            r"\bdebit\s+card\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in financial_patterns
        )

    @staticmethod
    def _check_special_characters(text: str) -> bool:
        """
        Detect excessive special characters or repeated punctuation.
        """

        special_characters = re.findall(
            r"[!$%^*_=+<>@#]",
            text,
        )

        repeated_punctuation = re.search(
            r"[!?]{3,}",
            text,
        )

        return (
            len(special_characters) >= 5
            or repeated_punctuation is not None
        )

    @staticmethod
    def _calculate_score(features: dict) -> float:
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
        score: float,
        status: str,
        risk: str,
        indicators: list,
        features: dict,
    ) -> dict:
        """
        Create a standardized analysis result.
        """

        return {
            "text": text,
            "score": score,
            "status": status,
            "risk_level": risk,
            "indicators": indicators,
            "features": features,
        }