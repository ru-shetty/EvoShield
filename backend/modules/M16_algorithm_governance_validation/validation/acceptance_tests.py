from typing import Dict


class AcceptanceTests:

    def __init__(
        self,
        minimum_confidence: float = 0.60,
        maximum_error_rate: float = 0.30,
        maximum_drift_frequency: float = 0.30,
        maximum_rollback_frequency: float = 0.20,
        maximum_trust_volatility: float = 0.30,
    ):

        self.minimum_confidence = minimum_confidence
        self.maximum_error_rate = maximum_error_rate
        self.maximum_drift_frequency = maximum_drift_frequency
        self.maximum_rollback_frequency = maximum_rollback_frequency
        self.maximum_trust_volatility = maximum_trust_volatility

    def evaluate(
        self,
        metrics: Dict[str, float],
    ) -> Dict[str, bool]:

        return {
            "confidence": (
                metrics.get("confidence", 0.0)
                >= self.minimum_confidence
            ),
            "error_rate": (
                metrics.get("error_rate", 1.0)
                <= self.maximum_error_rate
            ),
            "drift_frequency": (
                metrics.get("drift_frequency", 1.0)
                <= self.maximum_drift_frequency
            ),
            "rollback_frequency": (
                metrics.get("rollback_frequency", 1.0)
                <= self.maximum_rollback_frequency
            ),
            "trust_volatility": (
                metrics.get("trust_volatility", 1.0)
                <= self.maximum_trust_volatility
            ),
        }

    def passed(self, metrics: Dict[str, float]) -> bool:

        return all(self.evaluate(metrics).values())