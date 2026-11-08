"""Research clock-offset interval from authenticated four-timestamp exchange.

Receiver monotonic clock R = sender monotonic clock S + unknown offset.
With nonnegative one-way delays and timestamps:
 receiver sends request at R1, sender receives at S2,
 sender replies at S3, receiver receives at R4,
 offset is in [R1-S2, R4-S3].

Authenticated request/response and same session/nonce are prerequisites.
This estimator does not establish those prerequisites itself.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class FourTimestampExchange:
    receiver_request_s: float
    sender_received_s: float
    sender_replied_s: float
    receiver_reply_received_s: float
    authenticated_exchange: bool
    same_nonce_and_session: bool


@dataclass(frozen=True)
class OffsetInterval:
    lower_s: float
    upper_s: float
    width_s: float
    network_rtt_upper_s: float


def infer_offset_interval(
    e: FourTimestampExchange, *,
    max_rtt_s: float = 0.25,
    max_width_s: float = 0.1,
) -> OffsetInterval:
    """Derive conservative offset bounds; reject stale or mismatched evidence."""
    if not e.authenticated_exchange or not e.same_nonce_and_session:
        raise ValueError("unverified four-timestamp exchange")
    values = (
        e.receiver_request_s, e.sender_received_s,
        e.sender_replied_s, e.receiver_reply_received_s,
        max_rtt_s, max_width_s,
    )
    if not all(math.isfinite(v) for v in values):
        raise ValueError("invalid timing input")
    if max_rtt_s <= 0 or max_width_s < 0:
        raise ValueError("invalid timing tolerances")
    if (e.sender_replied_s < e.sender_received_s
        or e.receiver_reply_received_s < e.receiver_request_s):
        raise ValueError("nonmonotonic exchange timestamps")
    lower = e.receiver_request_s - e.sender_received_s
    upper = e.receiver_reply_received_s - e.sender_replied_s
    width = upper - lower
    if width < -1e-9:
        raise ValueError("negative implied network transit")
    if width < 0:
        width = 0.0
    if width > max_rtt_s or width > max_width_s:
        raise ValueError("timing uncertainty too large")
    return OffsetInterval(lower, upper, width, width)
