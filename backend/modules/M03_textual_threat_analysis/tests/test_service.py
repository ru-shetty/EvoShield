"""
Tests for the M03 textual threat analysis service.
"""

import unittest

from ..services.service import TextualThreatAnalysisService


class TestTextualThreatAnalysisService(unittest.TestCase):
    """Test cases for TextualThreatAnalysisService."""

    def setUp(self):
        self.service = TextualThreatAnalysisService()

    def test_analyze_safe_text(self):
        """The service should analyze normal text."""

        result = self.service.analyze_text(
            "Hello, have a nice day."
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.text,
            "Hello, have a nice day.",
        )

        self.assertEqual(
            result.status,
            "SAFE",
        )

    def test_analyze_suspicious_text(self):
        """The service should detect suspicious text."""

        result = self.service.analyze_text(
            "Please verify your account immediately."
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
            "Hello, have a nice day."
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
        """Each analysis should receive an entity ID."""

        result = self.service.analyze_text(
            "Test message."
        )

        self.assertTrue(
            result.entity_id.startswith("TEXT-")
        )

    def test_multiple_analyses_have_unique_ids(self):
        """Different analyses should have different entity IDs."""

        first = self.service.analyze_text(
            "First message."
        )

        second = self.service.analyze_text(
            "Second message."
        )

        self.assertNotEqual(
            first.entity_id,
            second.entity_id,
        )


if __name__ == "__main__":
    unittest.main()