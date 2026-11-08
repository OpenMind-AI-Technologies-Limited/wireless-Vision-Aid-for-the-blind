import pytest
from research.cluster_bootstrap import paired_cluster_bootstrap


def test_bootstrap_reproducible_and_clustered():
    rows = [
        ("run_a", True, True, True),
        ("run_a", False, True, False),
        ("run_b", True, True, False),
        ("run_b", False, True, False),
        ("run_c", True, True, True),
        ("run_c", False, False, False),
    ]
    a = paired_cluster_bootstrap(rows, replicates=200, seed=12)
    b = paired_cluster_bootstrap(rows, replicates=200, seed=12)
    assert a == b
    assert a["independent_run_count"] == 3
    assert a["delta_unsupported_per_frame"] == pytest.approx(-2 / 6)
    assert a["delta_valid_guidance_recall"] == pytest.approx(-1 / 3)


def test_bootstrap_requires_independent_runs():
    with pytest.raises(ValueError, match="at least two"):
        paired_cluster_bootstrap([("only", True, True, True)])


def test_bootstrap_all_negative_ground_truth_reports_no_recall():
    rows = [("a", False, True, False), ("b", False, True, False)]
    report = paired_cluster_bootstrap(rows, replicates=100)
    assert report["delta_valid_guidance_recall"] is None
    assert report["delta_valid_guidance_recall_ci95"] is None
