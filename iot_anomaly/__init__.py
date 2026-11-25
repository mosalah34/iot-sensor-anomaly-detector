"""Streaming anomaly detection for IoT sensor telemetry."""
from .detectors import EwmaZScoreDetector, RateOfChangeDetector, StuckValueDetector
from .simulate import simulate_temperature

__all__ = [
    "EwmaZScoreDetector",
    "RateOfChangeDetector",
    "StuckValueDetector",
    "simulate_temperature",
]
