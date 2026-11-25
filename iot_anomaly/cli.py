"""Command line: python -m iot_anomaly.cli [--csv FILE] """
from __future__ import annotations

import argparse
import csv

from .detectors import EwmaZScoreDetector, RateOfChangeDetector, StuckValueDetector
from .simulate import simulate_temperature


def run(rows):
    """rows: iterable of (index, value). Returns list of (index, value, detector, reason)."""
    detectors = {
        "ewma": EwmaZScoreDetector(alpha=0.05, threshold=5.0, warmup=30),
        "rate": RateOfChangeDetector(max_delta=3.0),
        "stuck": StuckValueDetector(max_repeats=10),
    }
    events = []
    for idx, value in rows:
        for name, det in detectors.items():
            reason = det.update(value)
            if reason:
                events.append((idx, value, name, reason))
    return events


def main(argv=None):
    p = argparse.ArgumentParser(description="Detect anomalies in sensor readings.")
    p.add_argument("--csv", help="CSV with a 'value' column. Default: built-in synthetic demo.")
    args = p.parse_args(argv)
    if args.csv:
        with open(args.csv, newline="") as f:
            rows = [(i, float(r["value"])) for i, r in enumerate(csv.DictReader(f))]
    else:
        print("Using synthetic demo data (not from a real sensor).")
        rows = [(i, v) for i, v, _ in simulate_temperature()]
    events = run(rows)
    for idx, value, name, reason in events:
        print(f"sample {idx:>4}  value {value:>6}  [{name}] {reason}")
    print(f"{len(events)} flagged samples out of {len(rows)}")


if __name__ == "__main__":
    main()
