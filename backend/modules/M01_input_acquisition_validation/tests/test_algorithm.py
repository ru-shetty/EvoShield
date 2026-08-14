"""
Tests for Module 1 input acquisition algorithm.
"""

import unittest

from ..processors.processor import InputProcessor


class TestInputAcquisitionAlgorithm(unittest.TestCase):

    def setUp(self):
        self.processor = InputProcessor()

    def test_identify_url(self):

        url = "https://example.com"

        result = self.processor.identify_input_type(url)

        self.assertEqual(result, "url")

    def test_identify_text(self):

        text = "Your account needs verification."

        result = self.processor.identify_input_type(text)

        self.assertEqual(result, "text")

    def test_validate_url(self):

        url = "https://example.com/login"

        result = self.processor.validate_url(url)

        self.assertTrue(result["valid"])

    def test_invalid_url(self):

        url = "not-a-valid-url"

        result = self.processor.validate_url(url)

        self.assertFalse(result["valid"])

    def test_entity_id_creation(self):

        entity_id = self.processor.create_entity_id()

        self.assertTrue(
            entity_id.startswith("ENT-")
        )


if __name__ == "__main__":
    unittest.main()