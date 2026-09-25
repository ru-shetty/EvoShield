from collections import deque


class RollbackMonitor:

    def __init__(self, window_size: int = 100):
        self.rollbacks = deque(maxlen=window_size)
        self.reanalysis = deque(maxlen=window_size)
        self.trust_values = deque(maxlen=window_size)

    def record_rollback(self, rollback: bool) -> None:

        self.rollbacks.append(1 if rollback else 0)

    def record_reanalysis(self, successful: bool) -> None:

        self.reanalysis.append(1 if successful else 0)

    def record_trust(self, trust_score: float) -> None:

        self.trust_values.append(float(trust_score))

    def rollback_frequency(self) -> float:

        if not self.rollbacks:
            return 0.0

        return sum(self.rollbacks) / len(self.rollbacks)

    def reanalysis_success_rate(self) -> float:

        if not self.reanalysis:
            return 0.0

        return sum(self.reanalysis) / len(self.reanalysis)

    def trust_volatility(self) -> float:

        if len(self.trust_values) < 2:
            return 0.0

        differences = [
            abs(self.trust_values[i] - self.trust_values[i - 1])
            for i in range(1, len(self.trust_values))
        ]

        return sum(differences) / len(differences)

    def metrics(self):

        return {
            "rollback_frequency": self.rollback_frequency(),
            "reanalysis_success_rate": self.reanalysis_success_rate(),
            "trust_volatility": self.trust_volatility(),
        }