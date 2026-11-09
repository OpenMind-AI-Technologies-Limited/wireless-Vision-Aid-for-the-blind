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
