from typing import Dict


class IntegrationValidator:

    REQUIRED_FIELDS = [
        "model_version",
        "preprocessor_version",
        "cluster_version",
        "drift_parameter_version",
    ]

    def validate_version_bundle(
        self,
        version_data: Dict,
    ) -> bool:

        return all(
            version_data.get(field)
            for field in self.REQUIRED_FIELDS
        )

    def validate_runtime_metrics(
        self,
        metrics: Dict,
    ) -> bool:

        required = [
            "confidence",
            "error_rate",
            "drift_frequency",
            "rollback_frequency",
            "false_positive_rate",
            "reanalysis_success_rate",
            "trust_volatility",
        ]

        return all(
            field in metrics
            for field in required
        )

    def validate(
        self,
        version_data: Dict,
        metrics: Dict,
    ) -> bool:

        return (
            self.validate_version_bundle(version_data)
            and self.validate_runtime_metrics(metrics)
        )