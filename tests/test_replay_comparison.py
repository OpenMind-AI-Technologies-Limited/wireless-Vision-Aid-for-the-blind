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
