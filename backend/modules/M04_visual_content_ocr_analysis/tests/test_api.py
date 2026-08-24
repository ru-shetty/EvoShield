"""
API tests for M04 - Visual Content OCR Analysis.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
    )
)

sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "test_settings",
)

import django

django.setup()

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from ..api.views import VisualContentOCRAnalysisView


class TestVisualContentOCRAnalysisAPI(SimpleTestCase):
    """Test cases for the visual content OCR analysis API."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = VisualContentOCRAnalysisView.as_view()

    def test_analyze_valid_text(self):
        """Valid OCR text should return a successful response."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": "Hello, welcome to our website.",
                "ocr_confidence": 0.95,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "entity_id",
            response.data,
        )

        self.assertIn(
            "text",
            response.data,
        )

        self.assertIn(
            "ocr_confidence",
            response.data,
        )

        self.assertIn(
            "score",
            response.data,
        )

        self.assertIn(
            "status",
            response.data,
        )

        self.assertIn(
            "risk_level",
            response.data,
        )

    def test_analyze_threatening_visual_text(self):
        """Threatening OCR text should be analyzed successfully."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": (
                    "URGENT! Your account has been suspended. "
                    "Verify your account immediately. "
                    "Enter your password and make a payment."
                ),
                "ocr_confidence": 0.90,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "suspicious_keyword",
            response.data["indicators"],
        )

        self.assertGreater(
            response.data["score"],
            0.0,
        )

    def test_low_ocr_confidence(self):
        """Low OCR confidence should be accepted and analyzed."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": "Some extracted text.",
                "ocr_confidence": 0.40,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "low_ocr_confidence",
            response.data["indicators"],
        )

    def test_missing_text(self):
        """Missing text should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "ocr_confidence": 0.90,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_empty_text(self):
        """Empty text should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": "",
                "ocr_confidence": 0.90,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_invalid_ocr_confidence(self):
        """OCR confidence outside 0-1 should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": "Sample OCR text.",
                "ocr_confidence": 1.5,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_whitespace_text(self):
        """Whitespace-only text should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": "   ",
                "ocr_confidence": 0.90,
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            400,
        )


if __name__ == "__main__":
    import unittest

    unittest.main()