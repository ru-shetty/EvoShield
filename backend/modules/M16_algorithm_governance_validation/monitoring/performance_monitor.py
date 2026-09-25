from collections import deque
from typing import Optional


class PerformanceMonitor:

    def __init__(self, window_size: int = 100):
        self.confidences = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        self.false_positives = deque(maxlen=window_size)

    def record(
        self,
        confidence: float,
        error: bool = False,
        false_positive: bool = False,
    ) -> None:

        self.confidences.append(float(confidence))
        self.errors.append(1 if error else 0)
        self.false_positives.append(1 if false_positive else 0)

    def average_confidence(self) -> float:

        if not self.confidences:
            return 0.0

        return sum(self.confidences) / len(self.confidences)

    def error_rate(self) -> float:

        if not self.errors:
            return 0.0

        return sum(self.errors) / len(self.errors)

    def false_positive_rate(self) -> float:

        if not self.false_positives:
            return 0.0

        return sum(self.false_positives) / len(self.false_positives)

    def metrics(self):

        return {
            "confidence": self.average_confidence(),
            "error_rate": self.error_rate(),
            "false_positive_rate": self.false_positive_rate(),
        }