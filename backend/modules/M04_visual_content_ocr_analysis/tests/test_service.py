"""
Tests for the M04 visual content OCR analysis service.
"""

import unittest

from ..services.service import VisualContentOCRAnalysisService


class TestVisualContentOCRAnalysisService(unittest.TestCase):
    """Test cases for VisualContentOCRAnalysisService."""

    def setUp(self):
        self.service = VisualContentOCRAnalysisService()

    def test_analyze_safe_text(self):
        """The service should analyze normal OCR text."""

        result = self.service.analyze_text(
            "Hello, welcome to our website.",
            ocr_confidence=0.95,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.text,
            "Hello, welcome to our website.",
        )

        self.assertEqual(
            result.status,
            "SAFE",
        )

    def test_analyze_suspicious_text(self):
        """The service should detect suspicious OCR content."""

        result = self.service.analyze_text(
            "Please verify your account immediately.",
            ocr_confidence=0.90,
        )

        self.assertIn(
            "suspicious_keyword",
            result.indicators,
        )

        self.assertGreater(
            result.score,
            0.0,
        )

    def test_analyze_text_to_dict(self):
        """The service should return a dictionary result."""

        result = self.service.analyze_text_to_dict(
            "Hello, welcome to our website.",
            ocr_confidence=0.95,
        )

        self.assertIsInstance(
            result,
            dict,
        )

        self.assertIn(
            "entity_id",
            result,
        )

        self.assertIn(
            "text",
            result,
        )

        self.assertIn(
            "ocr_confidence",
            result,
        )

        self.assertIn(
            "score",
            result,
        )

        self.assertIn(
            "status",
            result,
        )

        self.assertIn(
            "risk_level",
            result,
        )

    def test_entity_id_is_generated(self):
        """Each analysis should receive an OCR entity ID."""

        result = self.service.analyze_text(
            "Test OCR message.",
            ocr_confidence=0.90,
        )

        self.assertTrue(
            result.entity_id.startswith("OCR-")
        )

    def test_multiple_analyses_have_unique_ids(self):
        """Different analyses should have different entity IDs."""

        first = self.service.analyze_text(
            "First OCR message.",
        )

        second = self.service.analyze_text(
            "Second OCR message.",
        )

        self.assertNotEqual(
            first.entity_id,
            second.entity_id,
        )

    def test_ocr_confidence_is_preserved(self):
        """The supplied OCR confidence should be preserved."""

        result = self.service.analyze_text(
            "Sample OCR text.",
            ocr_confidence=0.75,
        )

        self.assertEqual(
            result.ocr_confidence,
            0.75,
        )


if __name__ == "__main__":
    unittest.main()