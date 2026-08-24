"""
Tests for the M04 visual content OCR analysis algorithm.
"""

import unittest

from ..algorithms.ocr_analyzer import VisualContentOCRAnalyzer


class TestVisualContentOCRAnalyzer(unittest.TestCase):
    """Test cases for VisualContentOCRAnalyzer."""

    def setUp(self):
        self.analyzer = VisualContentOCRAnalyzer()

    def test_safe_text(self):
        """Normal OCR text should have low risk."""

        result = self.analyzer.analyze(
            "Hello, welcome to our website.",
            ocr_confidence=0.95,
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
            "Please verify your account.",
            ocr_confidence=0.90,
        )

        self.assertIn(
            "suspicious_keyword",
            result["indicators"],
        )

        self.assertGreater(
            result["score"],
            0.0,
        )

    def test_suspicious_phrase(self):
        """Suspicious phrases should be detected."""

        result = self.analyzer.analyze(
            "Please verify your account immediately.",
            ocr_confidence=0.90,
        )

        self.assertIn(
            "suspicious_phrase",
            result["indicators"],
        )

    def test_low_ocr_confidence(self):
        """Low OCR confidence should be detected."""

        result = self.analyzer.analyze(
            "Some extracted text.",
            ocr_confidence=0.40,
        )

        self.assertIn(
            "low_ocr_confidence",
            result["indicators"],
        )

    def test_financial_content(self):
        """Financial content should be detected."""

        result = self.analyzer.analyze(
            "Please make a payment to your bank account.",
            ocr_confidence=0.90,
        )

        self.assertIn(
            "financial_content",
            result["indicators"],
        )

    def test_credential_content(self):
        """Credential-related content should be detected."""

        result = self.analyzer.analyze(
            "Enter your password and username.",
            ocr_confidence=0.90,
        )

        self.assertIn(
            "credential_content",
            result["indicators"],
        )

    def test_high_text_density(self):
        """Long OCR text should be detected."""

        long_text = "This is OCR content. " * 30

        result = self.analyzer.analyze(
            long_text,
            ocr_confidence=0.90,
        )

        self.assertIn(
            "high_text_density",
            result["indicators"],
        )

    def test_multiple_threat_indicators(self):
        """Multiple indicators should produce high risk."""

        result = self.analyzer.analyze(
            "URGENT! Your account has been suspended. "
            "Verify your account immediately. "
            "Enter your password and make a payment.",
            ocr_confidence=0.90,
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
        """Empty OCR text should be handled safely."""

        result = self.analyzer.analyze(
            "",
            ocr_confidence=1.0,
        )

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