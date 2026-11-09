"""Opt-in integration tests; no physical camera or human-outcome claims."""
from core.evidence_gate import GateConfig
from core.navigation_cevg_adapter import evaluate_local_navigation


def decide(**changes):
    params = dict(
        frame_read_monotonic=10.0,
        decision_monotonic=10.1,
        detections=[{"confidence": 0.85}],
        camera_source=0,
        localization_fresh=True,
        metric_calibrated=True,
        path_available=True,
        config=GateConfig(max_age_s=0.5, min_confidence=0.5),
    )
    params.update(changes)
    return evaluate_local_navigation(**params)


def test_local_frame_can_enable_guidance():
    assert decide().action == "GUIDE"


def test_remote_url_not_misrepresented_as_authenticated():
    assert decide(camera_source="rtsp://example.invalid/stream").reason == "unverified_camera_provenance"


def test_delayed_processing_abstains():
    assert decide(decision_monotonic=11.0).reason == "stale_observation"


def test_uncalibrated_path_abstains():
    assert decide(metric_calibrated=False).reason == "metric_calibration_missing"


def test_missing_path_abstains():
    assert decide(path_available=False).reason == "path_unavailable"


def test_no_detections_is_conservative_abstention():
    assert decide(detections=[]).reason == "low_confidence"
