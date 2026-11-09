"""Simulation reproducibility and oracle independence, not physical safety."""
from research.independent_scene_simulation import simulate


def test_simulation_reproducible_and_all_confusion_cases_accounted():
    first = simulate(277, 200, "mixed")
    second = simulate(277, 200, "mixed")
    assert first == second
    assert len(first) == 3
    for row in first:
        assert row["tp"] + row["fp"] + row["tn"] + row["fn"] == 200


def test_capture_bound_is_more_conservative_than_receiver_age_only():
    for scenario in ("nominal", "mixed", "burst"):
        rows = simulate(323, 500, scenario)
        base = next(x for x in rows if x["policy"] == "receiver_fresh")
        proposed = next(x for x in rows if x["policy"] == "capture_bound")
        assert proposed["tp"] <= base["tp"]
        assert proposed["fp"] <= base["fp"]
        assert proposed["abstention"] >= base["abstention"]


def test_unsupported_warning_remains_possible_with_capture_bound():
    rows = simulate(20261109, 2000, "mixed")
    proposed = next(x for x in rows if x["policy"] == "capture_bound")
    assert proposed["fp"] > 0  # Timing proof does not solve perception errors.
