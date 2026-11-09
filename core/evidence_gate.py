"""Experimental CEVG evidence gate for actionable metric/directional guidance.

This gate is not a certified safety controller. Authentication is established by
the transport layer; callers MUST NOT set authenticated=True for unverified remote
frames. For local captures, origin='local' expresses process-local provenance,
not cryptographic device attestation.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

Origin = Literal["local", "remote"]
Action = Literal["GUIDE", "ABSTAIN"]


@dataclass(frozen=True)
class Evidence:
    observed_at_monotonic: float
    evaluated_at_monotonic: float
    confidence: float
    origin: Origin
    authenticated: bool = False
    capture_time_verified: bool = False
    localization_fresh: bool = False
    metric_calibrated: bool = False
    path_available: bool = False


@dataclass(frozen=True)
class GateConfig:
    max_age_s: float = 0.5
    min_confidence: float = 0.5

    def __post_init__(self) -> None:
        if not math.isfinite(self.max_age_s) or self.max_age_s <= 0:
            raise ValueError("max_age_s must be finite and positive")
        if not math.isfinite(self.min_confidence) or not 0 <= self.min_confidence <= 1:
            raise ValueError("min_confidence must be a probability")


@dataclass(frozen=True)
class Decision:
    action: Action
    reason: str
    age_s: float | None


def evaluate(e: Evidence, config: GateConfig = GateConfig()) -> Decision:
    """Return first deterministic reason that actionable guidance is prohibited.

    Timestamps must share a monotonic clock. This does NOT establish remote camera
    capture age; that requires authenticated sender timing and clock mapping.
    """
    timestamps = (e.observed_at_monotonic, e.evaluated_at_monotonic)
    if not all(math.isfinite(x) for x in timestamps):
        return Decision("ABSTAIN", "invalid_timestamp", None)
    age = e.evaluated_at_monotonic - e.observed_at_monotonic
    if age < 0:
        return Decision("ABSTAIN", "future_timestamp", age)
    if e.origin not in ("local", "remote"):
        return Decision("ABSTAIN", "untrusted_origin", age)
    if e.origin == "remote" and not e.authenticated:
        return Decision("ABSTAIN", "unauthenticated_remote_frame", age)
    if e.origin == "remote" and not e.capture_time_verified:
        return Decision("ABSTAIN", "unverified_remote_capture_time", age)
    if age > config.max_age_s:
        return Decision("ABSTAIN", "stale_observation", age)
    if not math.isfinite(e.confidence) or not 0 <= e.confidence <= 1:
        return Decision("ABSTAIN", "invalid_confidence", age)
    if e.confidence < config.min_confidence:
        return Decision("ABSTAIN", "low_confidence", age)
    if not e.localization_fresh:
        return Decision("ABSTAIN", "localization_invalid", age)
    if not e.metric_calibrated:
        return Decision("ABSTAIN", "metric_calibration_missing", age)
    if not e.path_available:
        return Decision("ABSTAIN", "path_unavailable", age)
    return Decision("GUIDE", "evidence_valid", age)
