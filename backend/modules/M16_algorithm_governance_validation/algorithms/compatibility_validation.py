from typing import Any, Dict


class CompatibilityValidator:
    """
    Validates feature schema and preprocessing compatibility.
    """

    def validate_feature_schema(
        self,
        expected_schema: Dict[str, Any],
        candidate_schema: Dict[str, Any],
    ) -> bool:

        if not isinstance(expected_schema, dict):
            return False

        if not isinstance(candidate_schema, dict):
            return False

        expected_features = expected_schema.get("features", [])
        candidate_features = candidate_schema.get("features", [])

        return expected_features == candidate_features

    def validate_scaler_encoder(
        self,
        model_metadata: Dict[str, Any],
        preprocessing_metadata: Dict[str, Any],
    ) -> bool:

        if not model_metadata or not preprocessing_metadata:
            return False

        expected_scaler = model_metadata.get("scaler_version")
        candidate_scaler = preprocessing_metadata.get("scaler_version")

        expected_encoder = model_metadata.get("encoder_version")
        candidate_encoder = preprocessing_metadata.get("encoder_version")

        scaler_ok = (
            expected_scaler is None
            or expected_scaler == candidate_scaler
        )

        encoder_ok = (
            expected_encoder is None
            or expected_encoder == candidate_encoder
        )

        return scaler_ok and encoder_ok

    def validate(
        self,
        expected_schema: Dict[str, Any],
        candidate_schema: Dict[str, Any],
        model_metadata: Dict[str, Any],
        preprocessing_metadata: Dict[str, Any],
    ) -> bool:

        schema_ok = self.validate_feature_schema(
            expected_schema,
            candidate_schema,
        )

        preprocessing_ok = self.validate_scaler_encoder(
            model_metadata,
            preprocessing_metadata,
        )

        return schema_ok and preprocessing_ok