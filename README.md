# iot-sensor-anomaly-detector

Small, dependency-free Python detectors that flag bad readings in a stream of IoT sensor data. The same code can run on a laptop, a Raspberry Pi, or a gateway that receives telemetry from ESP32 boards.

Three detectors, each with a one-line `update(value)` API:

| Detector | Catches | Idea |
|---|---|---|
| `EwmaZScoreDetector` | spikes and outliers | z-score against an exponentially weighted mean and variance; flagged samples do not poison the baseline; a sustained shift is accepted as a new level after `recover` samples |
| `RateOfChangeDetector` | sudden jumps | absolute difference between consecutive samples |
| `StuckValueDetector` | frozen sensors | same exact value repeated N times (loose wire, hung driver) |

## Run the demo

```bash
python -m iot_anomaly.cli                 # built-in synthetic data
python -m iot_anomaly.cli --csv my.csv    # CSV with a "value" column
```

The demo data is **synthetic**: a sine wave plus noise with three injected faults (a spike, a short level shift, a stuck sensor). It is not from a real device. Output of the default run:

```
sample  180  value  32.36  [ewma] zscore 13.9 > 5.0
sample  180  value  32.36  [rate] jump 9.17 > 3.0
sample  181  value  23.33  [rate] jump 9.03 > 3.0
sample  330  value  28.67  [rate] jump 6.43 > 3.0
sample  360  value  22.14  [rate] jump 5.87 > 3.0
sample  489  value  26.73  [stuck] stuck at 26.73 for 10 samples
sample  505  value  24.57  [ewma] zscore 5.3 > 5.0
...
11 flagged samples out of 600
```

## Use as a library

```python
from iot_anomaly import EwmaZScoreDetector

det = EwmaZScoreDetector(alpha=0.05, threshold=5.0, warmup=30)
for value in readings:
    reason = det.update(value)
    if reason:
        print("anomaly:", reason)
```

## Tests

```bash
pip install pytest
pytest
```

Tests cover each detector and check that the demo pipeline finds all three injected faults without unrelated false alarms.

## Limits

- Thresholds in `cli.py` are tuned for the synthetic demo. Tune them on your own data.
- The EWMA detector can miss a level shift that the rate detector catches, and the reverse; that is why the CLI runs all three.
- There is no MQTT or serial input yet. Feed it values from whatever transport you use.
- Not tested on real hardware.
