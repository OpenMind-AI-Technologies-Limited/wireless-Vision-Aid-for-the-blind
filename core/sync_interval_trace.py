"""Privacy-minimal authenticated clock-offset research evidence recorder."""
from __future__ import annotations

import csv
import os
from pathlib import Path

FIELDS = (
    "session_id", "receiver_reply_received_monotonic_s",
    "receiver_minus_sender_offset_lower_s",
    "receiver_minus_sender_offset_upper_s",
    "offset_interval_width_s",
)


def write_sync_interval(path, *, session_id, receiver_reply_received_monotonic_s,
                        receiver_minus_sender_offset_lower_s,
                        receiver_minus_sender_offset_upper_s):
    if not path:
        raise ValueError("sync trace path required")
    low = float(receiver_minus_sender_offset_lower_s)
    high = float(receiver_minus_sender_offset_upper_s)
    if low > high:
        raise ValueError("invalid offset bounds")
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    is_new = not dest.exists() or dest.stat().st_size == 0
    fd = os.open(str(dest), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "session_id": session_id,
            "receiver_reply_received_monotonic_s": receiver_reply_received_monotonic_s,
            "receiver_minus_sender_offset_lower_s": low,
            "receiver_minus_sender_offset_upper_s": high,
            "offset_interval_width_s": high - low,
        })
