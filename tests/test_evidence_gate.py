"""Deterministic CEVG gate validation; synthetic inputs, not physical-device tests."""
import math
from dataclasses import replace
import pytest

from core.evidence_gate import Evidence, GateConfig, evaluate


@pytest.fixture
def good():
    return Evidence(
        observed_at_monotonic=10.0,
        evaluated_at_monotonic=10.2,
        confidence=0.8,
        origin="local",
        localization_fresh=True,
        metric_calibrated=True,
        path_available=True,
    )


def test_valid_local_evidence(good):
    assert evaluate(good).action == "GUIDE"


@pytest.mark.parametrize("changes,reason", [
    ({"origin": "remote"}, "unauthenticated_remote_frame"),
    ({"evaluated_at_monotonic": 11.0}, "stale_observation"),
    ({"evaluated_at_monotonic": 9.0}, "future_timestamp"),
    ({"confidence": 0.1}, "low_confidence"),
    ({"confidence": math.nan}, "invalid_confidence"),
    ({"localization_fresh": False}, "localization_invalid"),
    ({"metric_calibrated": False}, "metric_calibration_missing"),
    ({"path_available": False}, "path_unavailable"),
])
def test_rejections(good, changes, reason):
    d = evaluate(replace(good, **changes))
    assert d.action == "ABSTAIN"
    assert d.reason == reason


def test_authenticated_remote_without_capture_proof_abstains(good):
    assert evaluate(replace(good, origin="remote", authenticated=True)).reason == "unverified_remote_capture_time"


def test_authenticated_remote_with_capture_proof_eligible(good):
    assert evaluate(replace(good, origin="remote", authenticated=True, capture_time_verified=True)).action == "GUIDE"


def test_remote_capture_age_not_inferred(good):
    # A receiver arrival timestamp must not be mislabeled a camera capture timestamp.
    assert evaluate(replace(good, origin="remote", authenticated=False)).action == "ABSTAIN"


def test_threshold_boundaries(good):
    assert evaluate(replace(good, confidence=0.5, evaluated_at_monotonic=10.5)).action == "GUIDE"
    assert evaluate(replace(good, evaluated_at_monotonic=10.500001)).action == "ABSTAIN"


def test_invalid_config():
    with pytest.raises(ValueError):
        GateConfig(max_age_s=0)
    with pytest.raises(ValueError):
        GateConfig(min_confidence=1.1)
