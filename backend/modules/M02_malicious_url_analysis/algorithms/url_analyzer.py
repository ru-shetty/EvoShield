"""
Malicious URL analysis algorithm for M02.

Uses the trained character-level TF-IDF URL classifier.
"""

from pathlib import Path
from urllib.parse import urlparse

import joblib

from ..config import (
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
    Analyzes URLs using the trained machine-learning model.
    """

    def __init__(self):
        """
        Load the trained model and TF-IDF vectorizer.
        """

        model_path = (
            Path(__file__).resolve().parent
            / "artifacts"
            / "url_model.joblib"
        )

        if not model_path.exists():
            raise FileNotFoundError(
                f"Trained URL model not found at: {model_path}"
            )

        saved_model = joblib.load(model_path)

        self.model = saved_model["model"]
        self.vectorizer = saved_model["vectorizer"]

    # ----------------------------------------------------------------
    # Main analysis
    # ----------------------------------------------------------------

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

        # ------------------------------------------------------------
        # Safely parse URL
        # ------------------------------------------------------------

        parsed_url = self._safe_parse_url(url)

        # ------------------------------------------------------------
        # Create TF-IDF representation
        # ------------------------------------------------------------

        cleaned_url = url.lower()

        vectorized_url = self.vectorizer.transform(
            [cleaned_url]
        )

        # ------------------------------------------------------------
        # Predict malicious probability
        # ------------------------------------------------------------

        probability = float(
            self.model.predict_proba(
                vectorized_url
            )[0][1]
        )

        score = round(
            probability,
            4,
        )

        # ------------------------------------------------------------
        # Generate human-readable indicators
        # ------------------------------------------------------------

        indicators = []

        if self._check_https(parsed_url):
            indicators.append("https")

        if self._check_ip_address(parsed_url):
            indicators.append("ip_address")

        if self._check_url_length(url):
            indicators.append("url_length")

        if self._check_keywords(url):
            indicators.append("suspicious_keyword")

        if self._check_special_characters(url):
            indicators.append("special_character")

        if self._check_extension(parsed_url):
            indicators.append("suspicious_extension")

        if self._check_scheme(parsed_url):
            indicators.append("suspicious_scheme")

        # ------------------------------------------------------------
        # Determine risk
        # ------------------------------------------------------------

        if score >= MALICIOUS_URL_SCORE_THRESHOLD:

            status = STATUS_MALICIOUS
            risk = RISK_HIGH

        elif score >= 0.50:

            status = STATUS_SUSPICIOUS
            risk = RISK_MEDIUM

        else:

            status = STATUS_SAFE
            risk = RISK_LOW

        # ------------------------------------------------------------
        # Feature information
        # ------------------------------------------------------------

        features = {
            "url_length": len(url),
            "has_https": int(
                parsed_url.scheme.lower() == "https"
            ),
            "has_ip_address": int(
                self._check_ip_address(parsed_url)
            ),
            "has_suspicious_keyword": int(
                self._check_keywords(url)
            ),
            "has_suspicious_extension": int(
                self._check_extension(parsed_url)
            ),
            "has_suspicious_scheme": int(
                self._check_scheme(parsed_url)
            ),
            "special_character_count": (
                self._count_special_characters(url)
            ),
        }

        return self._result(
            url=url,
            score=score,
            status=status,
            risk=risk,
            indicators=indicators,
            features=features,
        )

    # ----------------------------------------------------------------
    # URL parsing
    # ----------------------------------------------------------------

    @staticmethod
    def _safe_parse_url(url: str):

        if "://" not in url:
            url = "http://" + url

        try:

            return urlparse(url)

        except ValueError:

            return urlparse("http://")

    # ----------------------------------------------------------------
    # HTTPS
    # ----------------------------------------------------------------

    @staticmethod
    def _check_https(parsed_url) -> bool:
        """
        Detect URLs that do not use HTTPS.
        """

        return parsed_url.scheme.lower() != "https"

    # ----------------------------------------------------------------
    # IP address
    # ----------------------------------------------------------------

    @staticmethod
    def _check_ip_address(parsed_url) -> bool:
        """
        Detect IP addresses used instead of domain names.
        """

        hostname = parsed_url.hostname

        if not hostname:
            return False

        try:

            import ipaddress

            ipaddress.ip_address(hostname)

            return True

        except ValueError:

            return False

    # ----------------------------------------------------------------
    # URL length
    # ----------------------------------------------------------------

    @staticmethod
    def _check_url_length(url: str) -> bool:

        return len(url) > SUSPICIOUS_URL_LENGTH

    # ----------------------------------------------------------------
    # Suspicious keywords
    # ----------------------------------------------------------------

    @staticmethod
    def _check_keywords(url: str) -> bool:

        url_lower = url.lower()

        return any(
            keyword.lower() in url_lower
            for keyword in SUSPICIOUS_KEYWORDS
        )

    # ----------------------------------------------------------------
    # Special characters
    # ----------------------------------------------------------------

    @staticmethod
    def _count_special_characters(url: str) -> int:

        special_characters = set(
            "@%_=&?"
        )

        return sum(
            1
            for character in url
            if character in special_characters
        )

    @staticmethod
    def _check_special_characters(url: str) -> bool:

        return (
            MaliciousURLAnalyzer
            ._count_special_characters(url)
            >= 4
        )

    # ----------------------------------------------------------------
    # Suspicious extension
    # ----------------------------------------------------------------

    @staticmethod
    def _check_extension(parsed_url) -> bool:

        path = parsed_url.path.lower()

        return any(
            path.endswith(extension.lower())
            for extension in SUSPICIOUS_EXTENSIONS
        )

    # ----------------------------------------------------------------
    # Suspicious scheme
    # ----------------------------------------------------------------

    @staticmethod
    def _check_scheme(parsed_url) -> bool:

        return (
            parsed_url.scheme.lower()
            in {
                scheme.lower()
                for scheme in SUSPICIOUS_SCHEMES
            }
        )

    # ----------------------------------------------------------------
    # Standard response
    # ----------------------------------------------------------------

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
        Create the standard M02 response.
        """

        return {
            "url": url,
            "score": score,
            "status": status,
            "risk_level": risk,
            "indicators": indicators,
            "features": features or {},
        }