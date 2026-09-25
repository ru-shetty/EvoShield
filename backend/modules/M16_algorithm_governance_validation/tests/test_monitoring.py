from modules.M16_adaptive_algorithm_governance_and_validation.monitoring.performance_monitor import (
    PerformanceMonitor,
)
from modules.M16_adaptive_algorithm_governance_and_validation.monitoring.drift_monitor import (
    DriftMonitor,
)
from modules.M16_adaptive_algorithm_governance_and_validation.monitoring.rollback_monitor import (
    RollbackMonitor,
)


def test_performance_monitor():

    monitor = PerformanceMonitor()

    monitor.record(
        confidence=0.9,
        error=False,
        false_positive=False,
    )

    monitor.record(
        confidence=0.7,
        error=True,
        false_positive=True,
    )

    metrics = monitor.metrics()

    assert metrics["confidence"] == 0.8
    assert metrics["error_rate"] == 0.5
    assert metrics["false_positive_rate"] == 0.5


def test_drift_monitor():

    monitor = DriftMonitor()

    monitor.record(False)
    monitor.record(True)
    monitor.record(False)

    assert monitor.frequency() == 1 / 3


def test_rollback_monitor():

    monitor = RollbackMonitor()

    monitor.record_rollback(False)
    monitor.record_rollback(True)

    monitor.record_reanalysis(True)
    monitor.record_reanalysis(True)

    monitor.record_trust(1.0)
    monitor.record_trust(0.8)

    metrics = monitor.metrics()

    assert metrics["rollback_frequency"] == 0.5
    assert metrics["reanalysis_success_rate"] == 1.0
    assert metrics["trust_volatility"] == 0.2