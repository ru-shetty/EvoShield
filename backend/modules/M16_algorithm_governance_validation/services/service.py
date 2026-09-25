from typing import Dict, Optional

from ..algorithms.compatibility_validation import CompatibilityValidator
from ..models.version import (
    AlgorithmVersion,
    HealthMetrics,
    ValidationResult,
)
from ..monitoring.drift_monitor import DriftMonitor
from ..monitoring.performance_monitor import PerformanceMonitor
from ..monitoring.rollback_monitor import RollbackMonitor
from ..registry.algorithm_registry import AlgorithmRegistry
from ..validation.acceptance_tests import AcceptanceTests
from ..validation.offline_validation import OfflineValidator


class GovernanceService:

    def __init__(self):

        self.registry = AlgorithmRegistry()

        self.compatibility_validator = CompatibilityValidator()
        self.offline_validator = OfflineValidator()

        self.acceptance_tests = AcceptanceTests()

        self.performance_monitor = PerformanceMonitor()
        self.drift_monitor = DriftMonitor()
        self.rollback_monitor = RollbackMonitor()

        self.previous_approved_version: Optional[str] = None

    # --------------------------------------------------
    # CANDIDATE CREATION
    # --------------------------------------------------

    def create_candidate(
        self,
        model_version: str,
        preprocessor_version: str,
        cluster_version: str,
        drift_parameter_version: str,
        parameters: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> AlgorithmVersion:

        candidate = AlgorithmVersion(
            model_version=model_version,
            preprocessor_version=preprocessor_version,
            cluster_version=cluster_version,
            drift_parameter_version=drift_parameter_version,
            parameters=parameters or {},
            metadata=metadata or {},
        )

        self.registry.register(candidate)

        return candidate

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def validate_candidate(
        self,
        candidate: AlgorithmVersion,
        validation_data: Dict,
    ) -> ValidationResult:

        result = self.offline_validator.validate(
            validation_data
        )

        return result

    # --------------------------------------------------
    # DEPLOYMENT
    # --------------------------------------------------

    def deploy_candidate(
        self,
        candidate: AlgorithmVersion,
        validation_data: Dict,
    ) -> Dict:

        validation = self.validate_candidate(
            candidate,
            validation_data,
        )

        if not validation.passed:

            candidate.reject()

            return {
                "decision": "reject",
                "validation_status": validation.status,
                "version": candidate.version_id(),
                "errors": validation.errors,
                "warnings": validation.warnings,
            }

        active = self.registry.active()

        if active is not None:
            self.previous_approved_version = active.version_id()

        # Atomic approval/deployment
        candidate.approve()

        self.registry._active_version = candidate.version_id()

        return {
            "decision": "approve_and_deploy",
            "validation_status": validation.status,
            "version": candidate.version_id(),
            "previous_version": self.previous_approved_version,
        }

    # --------------------------------------------------
    # ROLLBACK
    # --------------------------------------------------

    def rollback(self) -> Dict:

        if not self.previous_approved_version:

            return {
                "decision": "rollback_unavailable"
            }

        previous = self.registry.get(
            self.previous_approved_version
        )

        if previous is None:

            return {
                "decision": "rollback_failed"
            }

        self.registry._active_version = (
            self.previous_approved_version
        )

        self.rollback_monitor.record_rollback(True)

        return {
            "decision": "rollback",
            "restored_version": previous.version_id(),
        }

    # --------------------------------------------------
    # RUNTIME MONITORING
    # --------------------------------------------------

    def record_runtime_event(
        self,
        confidence: float,
        error: bool = False,
        drift: bool = False,
        rollback: bool = False,
        false_positive: bool = False,
        reanalysis_success: bool = True,
        trust_score: float = 1.0,
    ) -> None:

        self.performance_monitor.record(
            confidence=confidence,
            error=error,
            false_positive=false_positive,
        )

        self.drift_monitor.record(drift)

        self.rollback_monitor.record_rollback(
            rollback
        )

        self.rollback_monitor.record_reanalysis(
            reanalysis_success
        )

        self.rollback_monitor.record_trust(
            trust_score
        )

    # --------------------------------------------------
    # HEALTH METRICS
    # --------------------------------------------------

    def health_metrics(self) -> HealthMetrics:

        performance = self.performance_monitor.metrics()
        drift = self.drift_monitor.metrics()
        rollback = self.rollback_monitor.metrics()

        return HealthMetrics(
            confidence=performance["confidence"],
            error_rate=performance["error_rate"],
            drift_frequency=drift["drift_frequency"],
            rollback_frequency=rollback["rollback_frequency"],
            false_positive_rate=performance[
                "false_positive_rate"
            ],
            reanalysis_success_rate=rollback[
                "reanalysis_success_rate"
            ],
            trust_volatility=rollback[
                "trust_volatility"
            ],
        )

    # --------------------------------------------------
    # RUNTIME HEALTH CHECK
    # --------------------------------------------------

    def health_status(self) -> Dict:

        metrics = self.health_metrics().as_dict()

        acceptance = self.acceptance_tests.evaluate(
            metrics
        )

        return {
            "metrics": metrics,
            "checks": acceptance,
            "healthy": all(acceptance.values()),
            "active_version": (
                self.registry.active().version_id()
                if self.registry.active()
                else None
            ),
        }

    # --------------------------------------------------
    # ANALYSIS VERSION ATTACHMENT
    # --------------------------------------------------

    def attach_versions(
        self,
        analysis_record: Dict,
    ) -> Dict:

        active = self.registry.active()

        if active is None:
            analysis_record["versions"] = None
            return analysis_record

        analysis_record["versions"] = {
            "model_version": active.model_version,
            "preprocessor_version": (
                active.preprocessor_version
            ),
            "cluster_version": active.cluster_version,
            "drift_parameter_version": (
                active.drift_parameter_version
            ),
        }

        return analysis_record

    # --------------------------------------------------
    # CHANGE REQUEST
    # --------------------------------------------------

    def request_change(
        self,
        validation_data: Dict,
        model_version: str,
        preprocessor_version: str,
        cluster_version: str,
        drift_parameter_version: str,
        parameters: Optional[Dict] = None,
    ) -> Dict:

        candidate = self.create_candidate(
            model_version=model_version,
            preprocessor_version=preprocessor_version,
            cluster_version=cluster_version,
            drift_parameter_version=drift_parameter_version,
            parameters=parameters,
        )

        return self.deploy_candidate(
            candidate,
            validation_data,
        )