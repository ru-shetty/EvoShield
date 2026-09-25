from ..algorithms.compatibility_validation import CompatibilityValidator
from ..algorithms.model_validation import ModelValidator
from ..algorithms.parameter_validation import ParameterValidator
from ..models.version import ValidationResult


class OfflineValidator:

    def __init__(self):
        self.compatibility = CompatibilityValidator()
        self.model_validator = ModelValidator()
        self.parameter_validator = ParameterValidator()

    def validate(self, candidate):

        result = ValidationResult(passed=True)

        compatibility_ok = self.compatibility.validate(
            candidate["expected_schema"],
            candidate["candidate_schema"],
            candidate["model_metadata"],
            candidate["preprocessing_metadata"],
        )

        result.add_check(
            "feature_and_preprocessing_compatibility",
            compatibility_ok,
        )

        model_result = self.model_validator.validate_all(
            candidate["detector_metrics"],
            candidate["clustering_metrics"],
            candidate["drift_metrics"],
            candidate["audit_config"],
        )

        for name, value in model_result.checks.items():
            result.add_check(name, value)

        parameter_result = self.parameter_validator.validate(
            candidate.get("parameters", {}),
            candidate.get("parameter_ranges", {}),
        )

        for name, value in parameter_result.checks.items():
            result.add_check(
                f"parameter_{name}",
                value,
            )

        result.errors.extend(model_result.errors)
        result.errors.extend(parameter_result.errors)
        result.warnings.extend(parameter_result.warnings)

        result.passed = all(result.checks.values())

        return result