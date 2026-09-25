from modules.M16_adaptive_algorithm_governance_and_validation.models.version import (
    AlgorithmVersion,
)
from modules.M16_adaptive_algorithm_governance_and_validation.registry.algorithm_registry import (
    AlgorithmRegistry,
)


def test_registry():

    registry = AlgorithmRegistry()

    version = AlgorithmVersion(
        model_version="M1",
        preprocessor_version="P1",
        cluster_version="C1",
        drift_parameter_version="D1",
    )

    version_id = registry.register(version)

    assert registry.get(version_id) is version

    assert registry.approve(version_id)

    assert registry.active() is version
    assert version.is_approved()