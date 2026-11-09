"""Research-only fail-closed remote speech release policy.

A verified CaptureProof may only be supplied by an independently authenticated
sender/session+clock adapter. Caller-provided booleans are not a replacement for
verified transport. An absent proof always abstains.
"""
from __future__ import annotations

from core.evidence_gate import Decision, GateConfig
from core.remote_capture_proof import CaptureProof, remote_guidance_decision


def release_remote_guidance(
    proof: CaptureProof | None,
    *,
    confidence: float,
    localization_fresh: bool,
    metric_calibrated: bool,
    path_available: bool,
    config: GateConfig = GateConfig(),
) -> Decision:
    if proof is None:
        return Decision("ABSTAIN", "missing_verified_remote_capture_proof", None)
    return remote_guidance_decision(
        proof,
        confidence=confidence,
        localization_fresh=localization_fresh,
        metric_calibrated=metric_calibrated,
        path_available=path_available,
        config=config,
    )


def release_remote_obstacle_warning(
    proof: CaptureProof | None,
    *,
    confidence: float,
    config: GateConfig = GateConfig(),
) -> Decision:
    """Release *descriptive obstacle warnings*, not calibrated path guidance.

    Warning mode does not imply a safe path, metric geometry or localization.
    Only authenticated capture provenance, conservative freshness and detection
    confidence are checked. Do not call this function for GO/LEFT/RIGHT path
    directives or interpret it as navigational safety certification.
    """
    import math
    if proof is None:
        return Decision("ABSTAIN", "missing_verified_remote_capture_proof", None)
    if not all(math.isfinite(v) for v in (
        proof.sender_capture_s, proof.receiver_decision_s,
        proof.offset_lower_s, proof.offset_upper_s,
    )):
        return Decision("ABSTAIN", "invalid_remote_timing", None)
    if not proof.authenticated_frame or not proof.matched_session_and_frame:
        return Decision("ABSTAIN", "unverified_frame_provenance", None)
    if not proof.trusted_clock_mapping:
        return Decision("ABSTAIN", "unverified_clock_mapping", None)
    if proof.offset_upper_s < proof.offset_lower_s:
        return Decision("ABSTAIN", "invalid_offset_interval", None)
    if proof.offset_upper_s - proof.offset_lower_s > 0.1:
        return Decision("ABSTAIN", "clock_uncertainty_too_large", None)
    latest = proof.sender_capture_s + proof.offset_upper_s
    age = proof.receiver_decision_s - (proof.sender_capture_s + proof.offset_lower_s)
    if latest > proof.receiver_decision_s:
        return Decision("ABSTAIN", "capture_could_be_in_future", None)
    if age < 0 or age > config.max_age_s:
        return Decision("ABSTAIN", "stale_observation", age)
    if not math.isfinite(confidence) or confidence < config.min_confidence:
        return Decision("ABSTAIN", "low_confidence", age)
    return Decision("GUIDE", "fresh_authenticated_obstacle_warning", age)
