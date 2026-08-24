"""
Malicious URL analysis algorithm for M02.
"""

import ipaddress
import re
from urllib.parse import urlparse

from ..config import (
    FEATURE_WEIGHTS,
    MALICIOUS_URL_SCORE_THRESHOLD,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    STATUS_MALICIOUS,
    STATUS_SAFE,
    STATUS_SUSPICIOUS,
    SUSPICIOUS_EXTENSIONS,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_SCHEMES,
    SUSPICIOUS_URL_LENGTH,
)


class MaliciousURLAnalyzer:
    """
    Analyzes a URL and calculates a risk score based on
    suspicious URL characteristics.
    """

    def analyze(self, url: str) -> dict:
        """
        Analyze a URL and return its risk assessment.
        """

        if not isinstance(url, str) or not url.strip():
            return self._result(
                url=url,
                score=1.0,
                status=STATUS_MALICIOUS,
                risk=RISK_HIGH,
                indicators=["invalid_or_empty_url"],
            )

        url = url.strip()

        parsed_url = urlparse(url)

        indicators = []
        features = {}

        features["https"] = self._check_https(parsed_url)
        features["ip_address"] = self._check_ip_address(parsed_url)
        features["url_length"] = self._check_url_length(url)
        features["suspicious_keyword"] = self._check_keywords(url)
        features["special_character"] = self._check_special_characters(url)
        features["suspicious_extension"] = self._check_extension(parsed_url)
        features["suspicious_scheme"] = self._check_scheme(parsed_url)

        for feature_name, detected in features.items():
            if detected:
                indicators.append(feature_name)

        score = self._calculate_score(features)

        if score >= MALICIOUS_URL_SCORE_THRESHOLD:
            status = STATUS_MALICIOUS
            risk = RISK_HIGH
        elif score >= 0.50:
            status = STATUS_SUSPICIOUS
            risk = RISK_MEDIUM
        else:
            status = STATUS_SAFE
            risk = RISK_LOW

        return self._result(
            url=url,
            score=score,
            status=status,
            risk=risk,
            indicators=indicators,
            features=features,
        )

    @staticmethod
    def _check_https(parsed_url) -> bool:
        """
        HTTPS itself is not malicious.
        This feature is considered suspicious when HTTPS is absent.
        """
        return parsed_url.scheme.lower() != "https"

    @staticmethod
    def _check_ip_address(parsed_url) -> bool:
        """
        Detect whether the hostname is an IP address instead of
        a normal domain name.
        """
        hostname = parsed_url.hostname

        if not hostname:
            return False

        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            return False

    @staticmethod
    def _check_url_length(url: str) -> bool:
        return len(url) > SUSPICIOUS_URL_LENGTH

    @staticmethod
    def _check_keywords(url: str) -> bool:
        """
        Detect suspicious security/account-related keywords.
        """
        url_lower = url.lower()

        return any(
            keyword in url_lower
            for keyword in SUSPICIOUS_KEYWORDS
        )

    @staticmethod
    def _check_special_characters(url: str) -> bool:
        """
        Detect excessive special characters commonly observed
        in suspicious or obfuscated URLs.
        """
        special_characters = re.findall(
            r"[@%_=&]",
            url,
        )

        return len(special_characters) >= 4

    @staticmethod
    def _check_extension(parsed_url) -> bool:
        """
        Detect suspicious executable/script extensions.
        """
        path = parsed_url.path.lower()

        return any(
            path.endswith(extension)
            for extension in SUSPICIOUS_EXTENSIONS
        )

    @staticmethod
    def _check_scheme(parsed_url) -> bool:
        """
        Detect suspicious URL schemes such as javascript,
        data, and file.
        """
        return parsed_url.scheme.lower() in SUSPICIOUS_SCHEMES

    @staticmethod
    def _calculate_score(features: dict) -> float:
        """
        Calculate the weighted maliciousness score.
        """
        score = 0.0

        for feature_name, detected in features.items():
            if detected:
                score += FEATURE_WEIGHTS.get(feature_name, 0.0)

        return round(min(score, 1.0), 4)

    @staticmethod
    def _result(
        url: str,
        score: float,
        status: str,
        risk: str,
        indicators: list,
        features: dict | None = None,
    ) -> dict:
        """
        Create a standardized analysis result.
        """
        return {
            "url": url,
            "score": score,
            "status": status,
            "risk_level": risk,
            "indicators": indicators,
            "features": features or {},
        }