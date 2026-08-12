# M13_cross_modal_feature_standardization/tests/test_service.py

from django.test import SimpleTestCase

from unittest.mock import patch

from ..services.service import (
    CrossModalFeatureService
)


class TestModule13Service(SimpleTestCase):

    @patch(
        "M13_cross_modal_feature_standardization"
        ".services.service"
        ".CrossModalFeatureProcessor"
    )
    def test_standardize(
        self,
        mock_processor
    ):

        mock_processor.return_value.process.return_value = {

            "EntityID": "EVS-001",

            "FeatureVector": [0.1, 0.2],

            "FeatureVectorSize": 2,

            "PreprocessingVersion":
                "M13-PREPROCESSING-v1",

            "SchemaVersion":
                "M13-SCHEMA-v1",

            "MissingFeatures": [],

            "Timestamp":
                "2026-01-01T00:00:00"
        }

        service = CrossModalFeatureService()

        result = service.standardize(

            entity_id="EVS-001",

            module_outputs={
                "url": {
                    "url_length": 100
                }
            }
        )

        self.assertEqual(
            result["EntityID"],
            "EVS-001"
        )