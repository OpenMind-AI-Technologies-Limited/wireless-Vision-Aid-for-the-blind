"""Experimental conservative remote capture-time proof.

An authenticated frame is insufficient to establish capture freshness. A trusted
clock mapping must additionally bound receiver minus sender monotonic clock
offset. This module deliberately does not perform device key verification or
clock synchronization; only a verified transport/synchronization adapter may
supply trusted=True and matched=True. Do not accept these fields from packets.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from core.evidence_gate import Decision, Evidence, GateConfig, evaluate
from core.clock_offset_bounds import FourTimestampExchange, infer_offset_interval


@dataclass(frozen=True)
class CaptureProof:
    sender_capture_s: float
    receiver_decision_s: float
    # Receiver clock = sender clock + offset; true offset lies in this interval.
    offset_lower_s: float
    offset_upper_s: float
    trusted_clock_mapping: bool
    authenticated_frame: bool
    matched_session_and_frame: bool


def remote_guidance_decision(
    proof: CaptureProof,
    *,
    confidence: float,
    localization_fresh: bool,
    metric_calibrated: bool,
    path_available: bool,
    config: GateConfig = GateConfig(),
    max_offset_uncertainty_s: float = 0.1,
) -> Decision:
    """Fail closed unless the worst-case capture age is within max_age_s."""
    values = (
        proof.sender_capture_s, proof.receiver_decision_s,
        proof.offset_lower_s, proof.offset_upper_s,
        max_offset_uncertainty_s,
    )
    if not all(math.isfinite(v) for v in values):
        return Decision("ABSTAIN", "invalid_remote_timing", None)
    if max_offset_uncertainty_s < 0:
        raise ValueError("max_offset_uncertainty_s must be nonnegative")
    if not proof.authenticated_frame or not proof.matched_session_and_frame:
        return Decision("ABSTAIN", "unverified_frame_provenance", None)
    if not proof.trusted_clock_mapping:
        return Decision("ABSTAIN", "unverified_clock_mapping", None)
    if proof.offset_lower_s > proof.offset_upper_s:
        return Decision("ABSTAIN", "invalid_offset_interval", None)
    if proof.offset_upper_s - proof.offset_lower_s > max_offset_uncertainty_s:
        return Decision("ABSTAIN", "clock_uncertainty_too_large", None)
    earliest_capture_receiver_s = proof.sender_capture_s + proof.offset_lower_s
    latest_capture_receiver_s = proof.sender_capture_s + proof.offset_upper_s
    if latest_capture_receiver_s > proof.receiver_decision_s:
        return Decision("ABSTAIN", "capture_could_be_in_future", None)
    # The lower offset bound maximizes elapsed age, conservatively.
    return evaluate(
        Evidence(
            observed_at_monotonic=earliest_capture_receiver_s,
            evaluated_at_monotonic=proof.receiver_decision_s,
            confidence=confidence,
            origin="remote",
            authenticated=True,
            capture_time_verified=True,
            localization_fresh=localization_fresh,
            metric_calibrated=metric_calibrated,
            path_available=path_available,
        ), config,
    )


def evaluate_remote_from_exchange(
    *,
    sender_capture_s: float,
    receiver_decision_s: float,
    exchange: FourTimestampExchange,
    frame_authenticated: bool,
    frame_matched_to_exchange_session: bool,
    confidence: float,
    localization_fresh: bool,
    metric_calibrated: bool,
    path_available: bool,
    config: GateConfig = GateConfig(),
    max_offset_uncertainty_s: float = 0.1,
    max_exchange_age_s: float = 5.0,
    clock_drift_ppm: float = 50.0,
) -> Decision:
    """Compose authenticated timing bounds, including bounded clock drift."""
    values = (receiver_decision_s, max_exchange_age_s, clock_drift_ppm)
    if not all(math.isfinite(v) for v in values) or max_exchange_age_s <= 0 or clock_drift_ppm < 0:
        return Decision("ABSTAIN", "invalid_sync_tolerances", None)
    exchange_age_s = receiver_decision_s - exchange.receiver_reply_received_s
    if not math.isfinite(exchange_age_s) or not 0 <= exchange_age_s <= max_exchange_age_s:
        return Decision("ABSTAIN", "stale_clock_exchange", None)
    try:
        interval = infer_offset_interval(
            exchange, max_width_s=max_offset_uncertainty_s
        )
    except ValueError:
        return Decision("ABSTAIN", "unverified_clock_exchange", None)
    drift_margin_s = exchange_age_s * clock_drift_ppm * 1e-6
    return remote_guidance_decision(
        CaptureProof(
            sender_capture_s=sender_capture_s,
            receiver_decision_s=receiver_decision_s,
            offset_lower_s=interval.lower_s - drift_margin_s,
            offset_upper_s=interval.upper_s + drift_margin_s,
            trusted_clock_mapping=True,
            authenticated_frame=frame_authenticated,
            matched_session_and_frame=frame_matched_to_exchange_session,
        ),
        confidence=confidence,
        localization_fresh=localization_fresh,
        metric_calibrated=metric_calibrated,
        path_available=path_available,
        config=config,
        max_offset_uncertainty_s=max_offset_uncertainty_s,
    )
