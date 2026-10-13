"""
Tests for the M02 malicious URL analysis algorithm.
"""

import unittest

from ..algorithms.url_analyzer import MaliciousURLAnalyzer


class TestMaliciousURLAnalyzer(unittest.TestCase):
    """Test cases for MaliciousURLAnalyzer."""

    def setUp(self):
        self.analyzer = MaliciousURLAnalyzer()

    def test_safe_https_url(self):
        """A normal HTTPS URL should have low risk."""

        result = self.analyzer.analyze(
            "https://example.com"
        )

        self.assertEqual(result["status"], "SAFE")
        self.assertEqual(result["risk_level"], "LOW")
        self.assertLess(result["score"], 0.50)

    def test_ip_address_url(self):
        """An IP-based URL should be detected as suspicious."""

        result = self.analyzer.analyze(
            "http://192.168.1.100/login"
        )

        self.assertIn(
            "ip_address",
            result["indicators"],
        )

        self.assertGreater(result["score"], 0.0)

    def test_suspicious_keyword(self):
        """Security-related keywords should be detected."""

        result = self.analyzer.analyze(
            "https://example.com/login/verify-account"
        )

        self.assertIn(
            "suspicious_keyword",
            result["indicators"],
        )

    def test_brand_lookalike_host_is_high_risk(self):
        result = self.analyzer.analyze(
            "https://micros0ft-login.example.invalid/account/verify"
        )

        self.assertEqual(result["risk_level"], "HIGH")
        self.assertIn("brand_lookalike", result["indicators"])
        self.assertEqual(result["features"]["brand_lookalike"], "microsoft")

    def test_known_brand_login_subdomain_is_not_flagged_by_keyword_alone(self):
        result = self.analyzer.analyze(
            "https://accounts.google.com/signin"
        )

        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["features"]["is_known_first_party_brand_host"], 1)

    def test_multiple_phishing_terms_raise_generic_fake_host(self):
        result = self.analyzer.analyze(
            "https://secure-login.example.invalid/account/verify"
        )

        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertGreaterEqual(result["score"], 0.50)

    def test_suspicious_extension(self):
        """Executable/script extensions should be detected."""

        result = self.analyzer.analyze(
            "https://example.com/download/file.exe"
        )

        self.assertIn(
            "suspicious_extension",
            result["indicators"],
        )

    def test_suspicious_scheme(self):
        """Suspicious URL schemes should be detected."""

        result = self.analyzer.analyze(
            "javascript:alert('test')"
        )

        self.assertIn(
            "suspicious_scheme",
            result["indicators"],
        )

    def test_long_url(self):
        """A very long URL should be detected."""

        long_url = (
            "https://example.com/"
            + ("a" * 200)
        )

        result = self.analyzer.analyze(long_url)

        self.assertIn(
            "url_length",
            result["indicators"],
        )

    def test_empty_url(self):
        """An empty URL should be handled safely."""

        result = self.analyzer.analyze("")

        self.assertEqual(
            result["status"],
            "MALICIOUS",
        )

        self.assertEqual(
            result["risk_level"],
            "HIGH",
        )


if __name__ == "__main__":
    unittest.main()
