from modules.M16_adaptive_algorithm_governance_and_validation.algorithms.parameter_validation import (
    ParameterValidator,
)


def test_parameter_validation_passes():

    validator = ParameterValidator()

    result = validator.validate(
        {
            "learning_rate": 0.01,
            "threshold": 0.5,
        },
        {
            "learning_rate": {
                "min": 0.001,
                "max": 0.1,
            },
            "threshold": {
                "min": 0.1,
                "max": 0.9,
            },
        },
    )

    assert result.passed is True


def test_parameter_validation_fails():

    validator = ParameterValidator()

    result = validator.validate(
        {
            "learning_rate": 1.0,
        },
        {
            "learning_rate": {
                "min": 0.001,
                "max": 0.1,
            },
        },
    )

    assert result.passed is False