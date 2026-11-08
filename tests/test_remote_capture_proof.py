"""Synthetic clock uncertainty and provenance cases; no field measurements."""
from dataclasses import replace

from core.evidence_gate import GateConfig
from core.remote_capture_proof import CaptureProof, remote_guidance_decision


def valid():
    return CaptureProof(
        sender_capture_s=10.0,
        receiver_decision_s=15.3,
        offset_lower_s=5.0,
        offset_upper_s=5.04,
        trusted_clock_mapping=True,
        authenticated_frame=True,
        matched_session_and_frame=True,
    )


def check(proof, **kwargs):
    return remote_guidance_decision(
        proof, confidence=0.9, localization_fresh=True,
        metric_calibrated=True, path_available=True,
        config=GateConfig(max_age_s=0.5), **kwargs,
    )


def test_bounded_clock_offset_allows_valid_guidance():
    assert check(valid()).action == "GUIDE"


def test_conservative_age_bound_rejects_stale_frame():
    assert check(replace(valid(), receiver_decision_s=15.6)).reason == "stale_observation"


def test_authenticated_frame_without_verified_clock_mapping_rejected():
    assert check(replace(valid(), trusted_clock_mapping=False)).reason == "unverified_clock_mapping"


def test_mismatched_frame_rejected_even_if_authenticated():
    assert check(replace(valid(), matched_session_and_frame=False)).reason == "unverified_frame_provenance"


def test_uncertainty_must_be_within_limit():
    assert check(replace(valid(), offset_upper_s=5.25)).reason == "clock_uncertainty_too_large"


def test_future_capture_interval_rejected():
    assert check(replace(valid(), receiver_decision_s=15.01)).reason == "capture_could_be_in_future"


def test_invalid_interval_rejected():
    assert check(replace(valid(), offset_lower_s=5.2)).reason == "invalid_offset_interval"


def test_authenticated_four_timestamp_exchange_can_bound_capture_age():
    from core.clock_offset_bounds import FourTimestampExchange
    from core.remote_capture_proof import evaluate_remote_from_exchange

    exchange = FourTimestampExchange(
        receiver_request_s=15.0, sender_received_s=10.02,
        sender_replied_s=10.03, receiver_reply_received_s=15.05,
        authenticated_exchange=True, same_nonce_and_session=True,
    )
    decision = evaluate_remote_from_exchange(
        sender_capture_s=10.1, receiver_decision_s=15.3,
        exchange=exchange, frame_authenticated=True,
        frame_matched_to_exchange_session=True,
        confidence=0.9, localization_fresh=True,
        metric_calibrated=True, path_available=True,
    )
    assert decision.action == "GUIDE"


def test_remote_exchange_uncertainty_abstains():
    from dataclasses import replace
    from core.clock_offset_bounds import FourTimestampExchange
    from core.remote_capture_proof import evaluate_remote_from_exchange

    exchange = FourTimestampExchange(
        receiver_request_s=15.0, sender_received_s=10.02,
        sender_replied_s=10.03, receiver_reply_received_s=15.5,
        authenticated_exchange=True, same_nonce_and_session=True,
    )
    result = evaluate_remote_from_exchange(
        sender_capture_s=10.1, receiver_decision_s=15.8,
        exchange=exchange, frame_authenticated=True,
        frame_matched_to_exchange_session=True, confidence=0.9,
        localization_fresh=True, metric_calibrated=True,
        path_available=True,
    )
    assert result.reason == "unverified_clock_exchange"
