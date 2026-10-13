"""
Malicious URL analysis algorithm for M02.

Uses the trained character-level TF-IDF URL classifier.
"""

import re
from pathlib import Path
from urllib.parse import urlparse

import joblib

from ..config import (
    FEATURE_WEIGHTS,
    MALICIOUS_URL_SCORE_THRESHOLD,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    SUSPICIOUS_URL_SCORE_THRESHOLD,
    STATUS_MALICIOUS,
    STATUS_SAFE,
    STATUS_SUSPICIOUS,
    SUSPICIOUS_EXTENSIONS,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_SCHEMES,
    SUSPICIOUS_URL_LENGTH,
)


# These are common brands attackers imitate in URL hosts. Keep this list
# conservative and allow known first-party domains to avoid flagging their
# normal subdomains. This is a heuristic, not a live reputation service.
_BRAND_DOMAINS = {
    "amazon": ("amazon.com", "amazon.in", "amazon.co.uk", "amazon.de"),
    "apple": ("apple.com", "icloud.com"),
    "facebook": ("facebook.com", "fb.com"),
    "google": ("google.com", "google.co.in", "google.co.uk", "google.ca"),
    "instagram": ("instagram.com",),
    "microsoft": ("microsoft.com", "microsoftonline.com", "live.com", "office.com", "outlook.com"),
    "netflix": ("netflix.com",),
    "paypal": ("paypal.com",),
    "whatsapp": ("whatsapp.com",),
    "yahoo": ("yahoo.com", "yahoo.co.in", "yahoo.co.uk"),
}
_COMMON_HOST_CONFUSABLES = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b"})


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

        self.model = None
        self.vectorizer = None
        if model_path.exists():
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

        cleaned_url = url.lower()

        # ------------------------------------------------------------
        # Generate human-readable indicators
        # ------------------------------------------------------------

        indicators = []

        if self._check_https(parsed_url):
            indicators.append("non_https")

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

        hostname = (parsed_url.hostname or "").lower().rstrip(".")
        host_keyword_count = self._keyword_count(hostname)
        keyword_count = self._keyword_count(url)
        path_keyword_count = self._keyword_count(
            parsed_url.path + "?" + parsed_url.query
        )
        impersonated_brand = self._impersonated_brand(hostname)
        trusted_brand_host = self._is_trusted_brand_host(hostname)
        has_userinfo = parsed_url.username is not None or parsed_url.password is not None
        has_punycode = any(label.startswith("xn--") for label in hostname.split("."))

        if host_keyword_count:
            indicators.append("suspicious_keyword_in_host")
        if impersonated_brand:
            indicators.append("brand_lookalike")
        if has_userinfo:
            indicators.append("url_userinfo")
        if has_punycode:
            indicators.append("punycode_host")

        if self.model is not None and self.vectorizer is not None:
            vectorized_url = self.vectorizer.transform([cleaned_url])
            model_score = float(self.model.predict_proba(vectorized_url)[0][1])
            score = max(
                model_score,
                self._rule_score(
                    indicators,
                    keyword_count=keyword_count,
                    host_keyword_count=host_keyword_count,
                    path_keyword_count=path_keyword_count,
                    trusted_brand_host=trusted_brand_host,
                ),
            )
            analysis_mode = "trained_model"
        else:
            # Keep first-run installs usable without treating this heuristic
            # score as a trained probability estimate. Explicit rules give
            # combinations of weak phishing signals a meaningful risk floor.
            score = self._rule_score(
                indicators,
                keyword_count=keyword_count,
                host_keyword_count=host_keyword_count,
                path_keyword_count=path_keyword_count,
                trusted_brand_host=trusted_brand_host,
            )
            analysis_mode = "heuristic_fallback"

        score = round(min(score, 1.0), 4)

        # ------------------------------------------------------------
        # Determine risk
        # ------------------------------------------------------------

        if score >= MALICIOUS_URL_SCORE_THRESHOLD:

            status = STATUS_MALICIOUS
            risk = RISK_HIGH

        elif score >= SUSPICIOUS_URL_SCORE_THRESHOLD:

            status = STATUS_SUSPICIOUS
            risk = RISK_MEDIUM

        else:

            status = STATUS_SAFE
            risk = RISK_LOW

        # ------------------------------------------------------------
        # Feature information
        # ------------------------------------------------------------

        features = {
            "analysis_mode": analysis_mode,
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
            "suspicious_keyword_count": keyword_count,
            "host_keyword_count": host_keyword_count,
            "has_brand_lookalike": int(bool(impersonated_brand)),
            "brand_lookalike": impersonated_brand or "",
            "is_known_first_party_brand_host": int(trusted_brand_host),
            "has_url_userinfo": int(has_userinfo),
            "has_punycode_host": int(has_punycode),
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

        if "://" not in url and not re.match(r"^[a-z][a-z0-9+.-]*:", url, flags=re.IGNORECASE):
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

    @staticmethod
    def _keyword_count(value: str) -> int:
        value_lower = value.lower()
        return sum(keyword.lower() in value_lower for keyword in SUSPICIOUS_KEYWORDS)

    @staticmethod
    def _impersonated_brand(hostname: str) -> str | None:
        """Return a known brand whose name appears in a non-first-party host."""
        if not hostname:
            return None

        normalized = hostname.translate(_COMMON_HOST_CONFUSABLES)
        compact_host = re.sub(r"[^a-z0-9]", "", normalized)
        for brand, official_domains in _BRAND_DOMAINS.items():
            if brand not in compact_host:
                continue
            if any(
                hostname == domain or hostname.endswith("." + domain)
                for domain in official_domains
            ):
                continue
            return brand
        return None

    @staticmethod
    def _is_trusted_brand_host(hostname: str) -> bool:
        return any(
            hostname == domain or hostname.endswith("." + domain)
            for official_domains in _BRAND_DOMAINS.values()
            for domain in official_domains
        )

    @staticmethod
    def _rule_score(
        indicators: list[str],
        *,
        keyword_count: int,
        host_keyword_count: int,
        path_keyword_count: int,
        trusted_brand_host: bool,
    ) -> float:
        score = sum(
            FEATURE_WEIGHTS.get(
                "https" if indicator == "non_https" else indicator,
                0.0,
            )
            for indicator in indicators
        )

        if "suspicious_scheme" in indicators:
            score = max(score, 0.95)
        if "brand_lookalike" in indicators:
            score = max(score, 0.85)
        if "url_userinfo" in indicators:
            score = max(score, 0.65)
        if "punycode_host" in indicators:
            score = max(score, 0.55)
        if "suspicious_extension" in indicators:
            score = max(score, 0.60)
        effective_keyword_count = path_keyword_count if trusted_brand_host else keyword_count
        effective_host_keyword_count = 0 if trusted_brand_host else host_keyword_count

        if "ip_address" in indicators and effective_keyword_count:
            score = max(score, 0.75)
        if effective_host_keyword_count:
            score = max(score, 0.55 if effective_host_keyword_count == 1 else 0.70)
        if effective_keyword_count >= 2:
            score = max(score, 0.50 if effective_keyword_count == 2 else 0.65)
        if len(indicators) >= 3:
            score = max(score, 0.50)

        return score

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
