# M13_cross_modal_feature_standardization/tests/test_algorithm.py

from django.test import SimpleTestCase

from ..algorithms import (
    collect_modality_features,
    map_to_common_schema,
    handle_missing_features,
    create_feature_vector
)

from ..config import (
    FEATURE_VECTOR_SIZE
)


class TestModule13Algorithm(SimpleTestCase):

    def test_collect_features(self):

        data = {

            "url": {
                "url_length": 100
            },

            "nlp": {
                "threat_score": 0.8
            }
        }

        result = collect_modality_features(
            data
        )

        self.assertEqual(
            result["url_length"],
            100
        )

        self.assertEqual(
            result["threat_score"],
            0.8
        )

    def test_common_schema(self):

        data = {

            "url_length": 100
        }

        result = map_to_common_schema(
            data
        )

        self.assertIn(
            "url_length",
            result
        )

        self.assertIn(
            "threat_score",
            result
        )

    def test_missing_features(self):

        data = {

            "url_length": None
        }

        filled, missing = (
            handle_missing_features(data)
        )

        self.assertEqual(
            filled["url_length"],
            0.0
        )

        self.assertIn(
            "url_length",
            missing
        )

    def test_fixed_vector_size(self):

        data = {}

        filled, _ = (
            handle_missing_features(data)
        )

        vector = create_feature_vector(
            filled
        )

        self.assertEqual(
            len(vector),
            FEATURE_VECTOR_SIZE
        )