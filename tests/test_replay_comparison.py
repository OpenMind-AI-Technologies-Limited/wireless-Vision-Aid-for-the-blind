"""Executable research replay metrics with independent ground-truth labels."""
from research.replay_comparison import metrics
from core.evidence_gate import Evidence, GateConfig


def sample(confidence=0.8, age=0.2, auth=True, calibrated=True):
    return Evidence(
        observed_at_monotonic=10.0,
        evaluated_at_monotonic=10.0 + age,
        confidence=confidence,
        origin="remote",
        authenticated=auth,
        capture_time_verified=True,
        localization_fresh=True,
        metric_calibrated=calibrated,
        path_available=True,
    )


def test_independent_labels_create_false_positive_and_false_negative():
    rows = [
        (sample(), True),
        (sample(auth=False), False),
        (sample(age=1), False),
        (sample(confidence=0.2), True),
        (sample(calibrated=False), False),
    ]
    report = metrics(rows, GateConfig())
    assert report["cevg"]["tp"] == 1
    assert report["cevg"]["fp"] == 0
    assert report["cevg"]["fn"] == 1
    assert report["confidence"]["fp"] == 3
    assert report["cevg"]["valid_guidance_recall"] == 0.5
    assert report["cevg"]["abstention_fraction"] == 0.8


def test_no_ground_truth_positive_returns_null_recall():
    report = metrics([(sample(auth=False), False)], GateConfig())
    assert report["cevg"]["valid_guidance_recall"] is None


def test_unverified_remote_capture_time_abstains_even_with_auth():
    row = sample()
    from dataclasses import replace
    report = metrics([(replace(row, capture_time_verified=False), True)], GateConfig())
    assert report["cevg"]["fn"] == 1
    assert report["cevg"]["tp"] == 0


def test_existing_navigation_baseline_matches_deployment_policy():
    rows = [
        (sample(confidence=0.1), True),
        (sample(calibrated=False), False),
        (sample(age=3.0), False),
    ]
    report = metrics(rows, GateConfig())
    # Existing navigation policy ignores frame age and detector confidence.
    assert report["existing_navigation"]["tp"] == 1
    assert report["existing_navigation"]["fp"] == 1
    assert report["existing_navigation"]["tn"] == 1
    assert report["existing_navigation"]["fn"] == 0
    assert report["existing_navigation"]["unsupported_fraction_of_all_cases"] == 1 / 3
    assert report["cevg"]["fn"] == 1


def test_trace_csv_loading_and_paired_report(tmp_path):
    import csv
    from research.replay_comparison import FIELDS, load_rows, paired_report
    path = tmp_path / "trace.csv"
    sample_rows = [
        dict(
            observed_at_monotonic="10", evaluated_at_monotonic="10.2",
            confidence="0.9", origin="remote", authenticated="1",
            capture_time_verified="1", localization_fresh="1",
            metric_calibrated="1", path_available="1",
            ground_truth_actionable="1",
        ),
        dict(
            observed_at_monotonic="10", evaluated_at_monotonic="12",
            confidence="0.9", origin="remote", authenticated="1",
            capture_time_verified="0", localization_fresh="1",
            metric_calibrated="1", path_available="1",
            ground_truth_actionable="0",
        ),
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sample_rows)
    rows = list(load_rows(path))
    result = paired_report(rows, GateConfig())
    assert result["baseline_only_unsupported"] == 1
    assert result["candidate_only_unsupported"] == 0
    assert metrics(rows, GateConfig())["cevg"]["valid_guidance_recall"] == 1.0
