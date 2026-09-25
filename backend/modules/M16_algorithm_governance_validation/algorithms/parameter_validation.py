from typing import Any, Dict

from ..models.version import ValidationResult


class ParameterValidator:

    def validate(
        self,
        parameters: Dict[str, Any],
        parameter_ranges: Dict[str, Any],
    ) -> ValidationResult:

        result = ValidationResult(passed=True)

        for name, value in parameters.items():

            if name not in parameter_ranges:
                result.add_warning(
                    f"No configured range for parameter: {name}"
                )
                continue

            rules = parameter_ranges[name]

            if "min" in rules and value < rules["min"]:
                result.add_error(
                    f"{name} is below minimum allowed value."
                )
                result.add_check(name, False)
                continue

            if "max" in rules and value > rules["max"]:
                result.add_error(
                    f"{name} is above maximum allowed value."
                )
                result.add_check(name, False)
                continue

            result.add_check(name, True)

        result.passed = all(result.checks.values()) if result.checks else True

        return result