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