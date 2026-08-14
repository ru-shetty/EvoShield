"""
Tests for Module 1 service layer.
"""

import unittest

from ..services.service import InputAcquisitionService


class TestInputAcquisitionService(unittest.TestCase):

    def setUp(self):
        self.service = InputAcquisitionService()

    def test_url_acquisition(self):

        result = self.service.acquire(
            "https://example.com"
        )

        self.assertEqual(
            result.entity_type,
            "url"
        )

        self.assertEqual(
            result.routing_decision,
            "malicious_url_analysis"
        )

        self.assertEqual(
            result.status,
            "QUEUED"
        )

    def test_text_acquisition(self):

        result = self.service.acquire(
            "Your account has been blocked."
        )

        self.assertEqual(
            result.entity_type,
            "text"
        )

        self.assertEqual(
            result.routing_decision,
            "textual_threat_analysis"
        )

    def test_text_input(self):

        result = self.service.acquire(
            "invalid-url"
        )

        self.assertEqual(
            result.entity_type,
            "text"
        )

        self.assertEqual(
            result.routing_decision,
            "textual_threat_analysis"
        )

        self.assertEqual(
            result.status,
            "QUEUED"
        )


if __name__ == "__main__":
    unittest.main()