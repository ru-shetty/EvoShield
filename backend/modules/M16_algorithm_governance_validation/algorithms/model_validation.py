from typing import Any, Dict

from ..models.version import ValidationResult


class ModelValidator:

    def validate_detector_performance(
        self,
        metrics: Dict[str, Any],
        minimum_accuracy: float = 0.70,
        maximum_error_rate: float = 0.30,
    ) -> bool:

        accuracy = float(metrics.get("accuracy", 0.0))
        error_rate = float(metrics.get("error_rate", 1.0))

        return (
            accuracy >= minimum_accuracy
            and error_rate <= maximum_error_rate
        )

    def validate_clustering_stability(
        self,
        metrics: Dict[str, Any],
        minimum_stability: float = 0.70,
    ) -> bool:

        stability = float(metrics.get("stability", 0.0))

        return stability >= minimum_stability

    def validate_drift_rollback(
        self,
        metrics: Dict[str, Any],
        maximum_drift_rate: float = 0.30,
        maximum_rollback_rate: float = 0.20,
    ) -> bool:

        drift_rate = float(metrics.get("drift_rate", 1.0))
        rollback_rate = float(metrics.get("rollback_rate", 1.0))

        return (
            drift_rate <= maximum_drift_rate
            and rollback_rate <= maximum_rollback_rate
        )

    def validate_audit_logging(
        self,
        audit_config: Dict[str, Any],
    ) -> bool:

        return bool(
            audit_config
            and audit_config.get("enabled", False)
        )

    def validate_all(
        self,
        detector_metrics: Dict[str, Any],
        clustering_metrics: Dict[str, Any],
        drift_metrics: Dict[str, Any],
        audit_config: Dict[str, Any],
    ) -> ValidationResult:

        result = ValidationResult(passed=True)

        result.add_check(
            "detector_performance",
            self.validate_detector_performance(detector_metrics),
        )

        result.add_check(
            "clustering_stability",
            self.validate_clustering_stability(clustering_metrics),
        )

        result.add_check(
            "drift_rollback",
            self.validate_drift_rollback(drift_metrics),
        )

        result.add_check(
            "audit_logging",
            self.validate_audit_logging(audit_config),
        )

        if not result.passed:
            result.add_error(
                "One or more model validation checks failed."
            )

        return result