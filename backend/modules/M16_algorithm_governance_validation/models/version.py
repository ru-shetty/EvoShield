from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AlgorithmVersion:
    model_version: str
    preprocessor_version: str
    cluster_version: str
    drift_parameter_version: str

    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    status: str = "candidate"
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

    def version_id(self) -> str:
        return (
            f"{self.model_version}:"
            f"{self.preprocessor_version}:"
            f"{self.cluster_version}:"
            f"{self.drift_parameter_version}"
        )

    def approve(self) -> None:
        self.status = "approved"
        self.approved_at = datetime.utcnow()

    def reject(self) -> None:
        self.status = "rejected"

    def is_approved(self) -> bool:
        return self.status == "approved"


@dataclass
class ValidationResult:
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def status(self) -> str:
        return "passed" if self.passed else "failed"

    def add_check(self, name: str, result: bool) -> None:
        self.checks[name] = result
        self.passed = all(self.checks.values())

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


@dataclass
class HealthMetrics:
    confidence: float = 0.0
    error_rate: float = 0.0
    drift_frequency: float = 0.0
    rollback_frequency: float = 0.0
    false_positive_rate: float = 0.0
    reanalysis_success_rate: float = 0.0
    trust_volatility: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "confidence": self.confidence,
            "error_rate": self.error_rate,
            "drift_frequency": self.drift_frequency,
            "rollback_frequency": self.rollback_frequency,
            "false_positive_rate": self.false_positive_rate,
            "reanalysis_success_rate": self.reanalysis_success_rate,
            "trust_volatility": self.trust_volatility,
        }