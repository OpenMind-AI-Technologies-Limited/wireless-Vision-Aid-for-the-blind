from research.sensitivity_grid import sweep


def test_sensitivity_sweep_is_deterministic_and_complete():
    a = sweep(runs=2, frames=20)
    b = sweep(runs=2, frames=20)
    assert a == b
    assert len(a) == 72
    assert {x["scenario"] for x in a} == {"nominal", "mixed", "burst"}
    assert {x["policy"] for x in a} == {"receiver_fresh", "capture_bound"}
