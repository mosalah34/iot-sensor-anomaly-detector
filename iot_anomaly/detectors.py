"""Small, dependency-free streaming detectors.

Each detector has an `update(value)` method that returns a reason string when
the sample looks anomalous, or None when it looks normal.
"""
from __future__ import annotations

import math


class EwmaZScoreDetector:
    """Flags samples far from an exponentially weighted moving average.

    Uses an EWMA of the mean and of the variance, so it adapts to slow drift
    but still reacts to sudden spikes. Anomalous samples do not update the
    baseline, so one spike does not hide the next one. If `recover` samples in
    a row are flagged, the shift is treated as a new normal level and the
    baseline moves to it.
    """

    def __init__(self, alpha: float = 0.1, threshold: float = 4.0, warmup: int = 20,
                 recover: int = 5):
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.alpha = alpha
        self.threshold = threshold
        self.warmup = warmup
        self.recover = recover
        self.streak = 0
        self.mean = 0.0
        self.var = 0.0
        self.count = 0

    def update(self, value: float):
        if self.count == 0:
            self.mean = value
            self.count = 1
            return None
        diff = value - self.mean
        std = math.sqrt(self.var)
        if self.count >= self.warmup and std > 1e-9:
            z = abs(diff) / std
            if z > self.threshold:
                self.streak += 1
                if self.streak >= self.recover:
                    self.mean = value
                    self.streak = 0
                return f"zscore {z:.1f} > {self.threshold}"
        self.streak = 0
        self.count += 1
        incr = self.alpha * diff
        self.mean += incr
        self.var = (1 - self.alpha) * (self.var + diff * incr)
        return None


class RateOfChangeDetector:
    """Flags a jump between consecutive samples larger than `max_delta`."""

    def __init__(self, max_delta: float):
        if max_delta <= 0:
            raise ValueError("max_delta must be positive")
        self.max_delta = max_delta
        self.last = None

    def update(self, value: float):
        prev, self.last = self.last, value
        if prev is not None and abs(value - prev) > self.max_delta:
            return f"jump {abs(value - prev):.2f} > {self.max_delta}"
        return None


class StuckValueDetector:
    """Flags a sensor that reports the exact same value too many times in a row.

    A frozen reading is a common failure mode (loose wire, hung driver).
    """

    def __init__(self, max_repeats: int = 10):
        if max_repeats < 2:
            raise ValueError("max_repeats must be at least 2")
        self.max_repeats = max_repeats
        self.last = None
        self.repeats = 0

    def update(self, value: float):
        if value == self.last:
            self.repeats += 1
        else:
            self.last = value
            self.repeats = 1
        if self.repeats == self.max_repeats:  # report once per episode
            return f"stuck at {value} for {self.repeats} samples"
        return None
