"""Opt-in local navigation CEVG adapter (not remote capture-time validation).

The existing navigation pipeline remains the production baseline. The adapter
uses a *receiver-side* frame-read monotonic timestamp. It must not be used
to claim camera exposure age or verified remote frame provenance.
"""
from __future__ import annotations

import math
from typing import Any

from core.evidence_gate import Decision, Evidence, GateConfig, evaluate


def evaluate_local_navigation(
    *,
    frame_read_monotonic: float,
    decision_monotonic: float,
    detections: list[dict[str, Any]],
    camera_source: Any,
    localization_fresh: bool,
    metric_calibrated: bool,
    path_available: bool,
    config: GateConfig,
) -> Decision:
    """Decide whether *experimental directional* guidance can be released.

    Only integer OpenCV device indexes are admitted as local provenance in
    this first adapter. Other sources cannot be declared authenticated here.
    Detector confidence is an object-detection surrogate, not a calibrated
    path-safety probability. Zero detections produce abstention by design.
    """
    local_device = type(camera_source) is int and camera_source >= 0
    if not local_device:
        return Decision("ABSTAIN", "unverified_camera_provenance", None)
    confidence = max(
        (float(d.get("confidence", 0.0)) for d in detections),
        default=0.0,
    )
    if not math.isfinite(confidence):
        confidence = float("nan")
    return evaluate(
        Evidence(
            observed_at_monotonic=frame_read_monotonic,
            evaluated_at_monotonic=decision_monotonic,
            confidence=confidence,
            origin="local",
            authenticated=False,
            localization_fresh=localization_fresh,
            metric_calibrated=metric_calibrated,
            path_available=path_available,
        ),
        config,
    )
