"""
Tests for Module 1 API.
"""

import unittest

from ..api.views import InputAcquisitionView


class TestInputAcquisitionAPI(unittest.TestCase):

    def setUp(self):
        self.view = InputAcquisitionView()

    def test_url_request(self):

        response = self.view.post(
            {
                "data": "https://example.com"
            }
        )

        self.assertTrue(
            response["success"]
        )

        self.assertEqual(
            response["data"]["entity_type"],
            "url"
        )

        self.assertEqual(
            response["data"]["routing_decision"],
            "malicious_url_analysis"
        )

    def test_text_request(self):

        response = self.view.post(
            {
                "data": "This is a suspicious message."
            }
        )

        self.assertTrue(
            response["success"]
        )

        self.assertEqual(
            response["data"]["entity_type"],
            "text"
        )

    def test_missing_data(self):

        response = self.view.post({})

        self.assertFalse(
            response["success"]
        )


if __name__ == "__main__":
    unittest.main()