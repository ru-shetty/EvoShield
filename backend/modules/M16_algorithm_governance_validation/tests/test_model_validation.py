from modules.M16_adaptive_algorithm_governance_and_validation.algorithms.model_validation import (
    ModelValidator,
)


def test_model_validation_passes():

    validator = ModelValidator()

    result = validator.validate_all(
        detector_metrics={
            "accuracy": 0.90,
            "error_rate": 0.10,
        },
        clustering_metrics={
            "stability": 0.90,
        },
        drift_metrics={
            "drift_rate": 0.10,
            "rollback_rate": 0.05,
        },
        audit_config={
            "enabled": True,
        },
    )

    assert result.passed is True


def test_model_validation_fails():

    validator = ModelValidator()

    result = validator.validate_all(
        detector_metrics={
            "accuracy": 0.40,
            "error_rate": 0.60,
        },
        clustering_metrics={
            "stability": 0.30,
        },
        drift_metrics={
            "drift_rate": 0.80,
            "rollback_rate": 0.60,
        },
        audit_config={
            "enabled": False,
        },
    )

    assert result.passed is False