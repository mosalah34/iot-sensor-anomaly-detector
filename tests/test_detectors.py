from iot_anomaly.cli import run
from iot_anomaly.detectors import EwmaZScoreDetector, RateOfChangeDetector, StuckValueDetector
from iot_anomaly.simulate import simulate_temperature


def test_ewma_flags_spike_not_noise():
    d = EwmaZScoreDetector(alpha=0.1, threshold=4, warmup=10)
    base = [20.0 + (0.1 if i % 2 else -0.1) for i in range(50)]
    assert all(d.update(v) is None for v in base)
    assert d.update(30.0) is not None


def test_ewma_spike_does_not_poison_baseline():
    d = EwmaZScoreDetector(alpha=0.1, threshold=4, warmup=10)
    for i in range(50):
        d.update(20.0 + (0.1 if i % 2 else -0.1))
    assert d.update(30.0) is not None
    assert d.update(30.0) is not None


def test_rate_of_change():
    d = RateOfChangeDetector(max_delta=2)
    assert d.update(10) is None
    assert d.update(11) is None
    assert d.update(15) is not None


def test_stuck_value():
    d = StuckValueDetector(max_repeats=3)
    assert d.update(5) is None
    assert d.update(5) is None
    assert d.update(5) is not None
    assert d.update(6) is None


def test_simulation_is_deterministic_and_labelled():
    a = simulate_temperature(seed=1)
    assert a == simulate_temperature(seed=1)
    assert {r[2] for r in a} >= {"spike", "jump", "stuck"}


def test_pipeline_finds_all_injected_faults():
    data = simulate_temperature()
    events = run([(i, v) for i, v, _ in data])
    flagged = {e[0] for e in events}
    for kind in ("spike", "jump", "stuck"):
        idxs = {i for i, _, lab in data if lab == kind}
        assert flagged & idxs, f"{kind} not detected"
    # Flags within 10 samples after an injected fault count as recovery, not noise.
    labelled = {i for i, _, lab in data if lab}
    near = {i + k for i in labelled for k in range(11)}
    assert not (flagged - near)


def test_ewma_accepts_sustained_level_shift():
    d = EwmaZScoreDetector(alpha=0.1, threshold=4, warmup=10, recover=5)
    for i in range(50):
        d.update(20.0 + (0.1 if i % 2 else -0.1))
    results = [d.update(30.0 + (0.1 if i % 2 else -0.1)) for i in range(30)]
    assert results[0] is not None
    assert results[-1] is None
