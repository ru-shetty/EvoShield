"""
API tests for M03 - Textual Threat Analysis.
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

from ..api.views import TextualThreatAnalysisView


class TestTextualThreatAnalysisAPI(SimpleTestCase):
    """Test cases for the textual threat analysis API."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TextualThreatAnalysisView.as_view()

    def test_analyze_valid_text(self):
        """A valid text should return a successful response."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": "Hello, have a nice day."
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

    def test_analyze_threatening_text(self):
        """Threatening text should be analyzed successfully."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": (
                    "URGENT! Your account has been suspended. "
                    "Verify your account immediately and "
                    "provide your password."
                )
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

    def test_missing_text(self):
        """A missing text field should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {},
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_empty_text(self):
        """An empty text field should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "text": ""
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
                "text": "   "
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