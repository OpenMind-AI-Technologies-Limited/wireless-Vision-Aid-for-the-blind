"""Property tests for the conservative authenticated-capture-age bound.

Mathematical validity assumes the real offset lies in the authenticated
clock-exchange interval; these tests do NOT establish device clock accuracy.
"""
import random

from core.evidence_gate import GateConfig
from core.remote_capture_proof import CaptureProof
from core.remote_guidance_release import release_remote_obstacle_warning


def test_verified_clock_interval_never_releases_physically_stale_sample():
    rng = random.Random(20261109)
    config = GateConfig(max_age_s=0.5, min_confidence=0.5)
    for _ in range(5000):
        true_offset = rng.uniform(-5, 5)
        sender_capture = rng.uniform(10, 500)
        real_age = rng.uniform(0, 1.5)
        lower = true_offset - rng.uniform(0, 0.03)
        upper = true_offset + rng.uniform(0, 0.03)
        decision_time = sender_capture + true_offset + real_age
        decision = release_remote_obstacle_warning(
            CaptureProof(
                sender_capture_s=sender_capture,
                receiver_decision_s=decision_time,
                offset_lower_s=lower,
                offset_upper_s=upper,
                trusted_clock_mapping=True,
                authenticated_frame=True,
                matched_session_and_frame=True,
            ),
            confidence=0.91,
            config=config,
        )
        if decision.action == "GUIDE":
            assert real_age <= config.max_age_s + 1e-9


def test_expired_frame_does_not_recover_from_high_confidence():
    config = GateConfig(max_age_s=0.25, min_confidence=0.8)
    proof = CaptureProof(
        sender_capture_s=10.0,
        receiver_decision_s=11.0,
        offset_lower_s=0.0,
        offset_upper_s=0.01,
        trusted_clock_mapping=True,
        authenticated_frame=True,
        matched_session_and_frame=True,
    )
    assert release_remote_obstacle_warning(
        proof, confidence=0.999, config=config,
    ).action == "ABSTAIN"
