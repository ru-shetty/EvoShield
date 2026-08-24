"""
Tests for the M03 textual threat analysis algorithm.
"""

import unittest

from ..algorithms.text_analyzer import TextualThreatAnalyzer


class TestTextualThreatAnalyzer(unittest.TestCase):
    """Test cases for TextualThreatAnalyzer."""

    def setUp(self):
        self.analyzer = TextualThreatAnalyzer()

    def test_safe_text(self):
        """Normal text should have low risk."""

        result = self.analyzer.analyze(
            "Hello, I hope you are having a great day."
        )

        self.assertEqual(
            result["status"],
            "SAFE",
        )

        self.assertEqual(
            result["risk_level"],
            "LOW",
        )

        self.assertLess(
            result["score"],
            0.40,
        )

    def test_suspicious_keyword(self):
        """Suspicious keywords should be detected."""

        result = self.analyzer.analyze(
            "Please verify your account immediately."
        )

        self.assertIn(
            "suspicious_keyword",
            result["indicators"],
        )

        self.assertGreater(
            result["score"],
            0.0,
        )

    def test_threat_phrase(self):
        """Known threat phrases should be detected."""

        result = self.analyzer.analyze(
            "Your account has been suspended. "
            "Verify your account."
        )

        self.assertIn(
            "threat_phrase",
            result["indicators"],
        )

    def test_urgency_indicator(self):
        """Urgency-related language should be detected."""

        result = self.analyzer.analyze(
            "Act now and verify your account immediately."
        )

        self.assertIn(
            "urgency_indicator",
            result["indicators"],
        )

    def test_credential_request(self):
        """Credential requests should be detected."""

        result = self.analyzer.analyze(
            "Please enter your password to confirm your login."
        )

        self.assertIn(
            "credential_request",
            result["indicators"],
        )

    def test_financial_request(self):
        """Financial requests should be detected."""

        result = self.analyzer.analyze(
            "Please send money and make a payment now."
        )

        self.assertIn(
            "financial_request",
            result["indicators"],
        )

    def test_special_characters(self):
        """Excessive special characters should be detected."""

        result = self.analyzer.analyze(
            "URGENT!!! $$$ Verify your account now!!!"
        )

        self.assertIn(
            "excessive_special_characters",
            result["indicators"],
        )

    def test_multiple_threat_indicators(self):
        """Multiple indicators should produce elevated risk."""

        result = self.analyzer.analyze(
            "URGENT!!! Your account has been suspended. "
            "Verify your account immediately and provide "
            "your password. Make a payment now!!!"
        )

        self.assertGreaterEqual(
            result["score"],
            0.70,
        )

        self.assertEqual(
            result["status"],
            "MALICIOUS",
        )

        self.assertEqual(
            result["risk_level"],
            "HIGH",
        )

    def test_empty_text(self):
        """Empty text should be handled safely."""

        result = self.analyzer.analyze("")

        self.assertEqual(
            result["status"],
            "MALICIOUS",
        )

        self.assertEqual(
            result["risk_level"],
            "HIGH",
        )

        self.assertIn(
            "empty_or_invalid_text",
            result["indicators"],
        )


if __name__ == "__main__":
    unittest.main()