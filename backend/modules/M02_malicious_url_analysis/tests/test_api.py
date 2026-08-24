"""
API tests for M02 - Malicious URL Analysis.
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

from ..api.views import MaliciousURLAnalysisView
class TestMaliciousURLAnalysisAPI(SimpleTestCase):
    """Test cases for the malicious URL analysis API."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = MaliciousURLAnalysisView.as_view()

    def test_analyze_valid_url(self):
        """A valid URL should return a successful response."""

        request = self.factory.post(
            "/analyze/",
            {
                "url": "https://example.com"
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
            "url",
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

    def test_invalid_url(self):
        """An invalid URL should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "url": "not-a-valid-url"
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_missing_url(self):
        """A missing URL should return HTTP 400."""

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

    def test_empty_url(self):
        """An empty URL should return HTTP 400."""

        request = self.factory.post(
            "/analyze/",
            {
                "url": ""
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