# M13_cross_modal_feature_standardization/tests/test_api.py

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from unittest.mock import patch


class TestModule13API(TestCase):

    def setUp(self):

        self.client = APIClient()

    @patch(
        "M13_cross_modal_feature_standardization"
        ".api.views"
        ".CrossModalFeatureService"
    )
    def test_standardize_api(
        self,
        mock_service
    ):

        mock_service.return_value.standardize.return_value = {

            "EntityID": "EVS-001",

            "FeatureVector": [0.0] * 27,

            "FeatureVectorSize": 27,

            "PreprocessingVersion":
                "M13-PREPROCESSING-v1",

            "SchemaVersion":
                "M13-SCHEMA-v1",

            "MissingFeatures": [],

            "Timestamp":
                "2026-01-01T00:00:00"
        }

        data = {

            "entity_id": "EVS-001",

            "url": {

                "url_length": 100,

                "url_entropy": 4.5,

                "url_risk_score": 0.8
            },

            "nlp": {

                "threat_score": 0.7,

                "urgency_score": 0.9
            },

            "ocr": {

                "ocr_threat_score": 0.6
            },

            "speech": {

                "speech_threat_score": 0.7
            },

            "malware": {

                "malware_risk_score": 0.5
            },

            "digital_arrest": {

                "payment_demand_score": 0.9
            }
        }

        response = self.client.post(
            "/api/m13/standardize/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )