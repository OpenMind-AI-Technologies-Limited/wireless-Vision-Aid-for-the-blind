"""Speech-release gate: fail closed without independently verified timing."""
from core.evidence_gate import GateConfig
from core.remote_guidance_release import release_remote_guidance
from core.remote_capture_proof import CaptureProof


def decision(proof):
    return release_remote_guidance(
        proof, confidence=0.9, localization_fresh=True,
        metric_calibrated=True, path_available=True,
        config=GateConfig(max_age_s=0.5),
    )


def test_no_capture_proof_abstains():
    assert decision(None).reason == "missing_verified_remote_capture_proof"


def test_unverified_clock_mapping_abstains():
    p = CaptureProof(
        sender_capture_s=10.0, receiver_decision_s=15.2,
        offset_lower_s=5.0, offset_upper_s=5.02,
        trusted_clock_mapping=False, authenticated_frame=True,
        matched_session_and_frame=True,
    )
    assert decision(p).reason == "unverified_clock_mapping"


def test_verified_proof_can_release_actionable_guidance():
    p = CaptureProof(
        sender_capture_s=10.0, receiver_decision_s=15.2,
        offset_lower_s=5.0, offset_upper_s=5.02,
        trusted_clock_mapping=True, authenticated_frame=True,
        matched_session_and_frame=True,
    )
    assert decision(p).action == "GUIDE"


def test_descriptive_warning_needs_verified_frame_and_freshness():
    from core.remote_guidance_release import release_remote_obstacle_warning
    from dataclasses import replace

    proof = CaptureProof(
        sender_capture_s=10.0, receiver_decision_s=15.2,
        offset_lower_s=5.0, offset_upper_s=5.02,
        trusted_clock_mapping=True, authenticated_frame=True,
        matched_session_and_frame=True,
    )
    assert release_remote_obstacle_warning(proof, confidence=0.9).action == "GUIDE"
    assert release_remote_obstacle_warning(
        replace(proof, authenticated_frame=False), confidence=0.9
    ).reason == "unverified_frame_provenance"
    assert release_remote_obstacle_warning(
        replace(proof, receiver_decision_s=16), confidence=0.9
    ).reason == "stale_observation"
    assert release_remote_obstacle_warning(
        proof, confidence=0.1
    ).reason == "low_confidence"
    assert release_remote_obstacle_warning(
        replace(proof, trusted_clock_mapping=False), confidence=0.9
    ).reason == "unverified_clock_mapping"
