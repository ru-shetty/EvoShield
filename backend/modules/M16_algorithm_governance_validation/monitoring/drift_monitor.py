from collections import deque


class DriftMonitor:

    def __init__(self, window_size: int = 100):
        self.events = deque(maxlen=window_size)

    def record(self, drift_detected: bool) -> None:

        self.events.append(1 if drift_detected else 0)

    def frequency(self) -> float:

        if not self.events:
            return 0.0

        return sum(self.events) / len(self.events)

    def is_unstable(self, threshold: float = 0.30) -> bool:

        return self.frequency() > threshold

    def metrics(self):

        return {
            "drift_frequency": self.frequency(),
            "unstable": self.is_unstable(),
        }