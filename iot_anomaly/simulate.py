"""Synthetic telemetry generator. The data is made up, not from a real device."""
from __future__ import annotations

import math
import random


def simulate_temperature(n: int = 600, seed: int = 7):
    """Return a list of (index, value, injected_label) tuples.

    A slow sine wave plus noise, with three injected faults: a one-sample
    spike, a short level shift (the "jump"), and a stuck sensor.
    """
    rng = random.Random(seed)
    rows = []
    stuck_from, stuck_len = int(n * 0.8), 25
    stuck_value = None
    for i in range(n):
        value = 25 + 3 * math.sin(2 * math.pi * i / 200) + rng.gauss(0, 0.15)
        label = ""
        if i == int(n * 0.3):
            value += 9
            label = "spike"
        if int(n * 0.55) <= i < int(n * 0.55) + 30:
            value += 6
            label = "jump"
        if stuck_from <= i < stuck_from + stuck_len:
            if stuck_value is None:
                stuck_value = round(value, 2)
            value = stuck_value
            label = "stuck"
        rows.append((i, round(value, 2), label))
    return rows
