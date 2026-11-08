"""Privacy-minimal experimental ESP32 capture-tick trace recorder."""
from __future__ import annotations

import csv
import os
from pathlib import Path

COLUMNS = (
    "session_id", "frame_id", "sender_capture_uptime_us",
    "receiver_decode_monotonic_s", "receiver_processing_end_monotonic_s",
)


def write_capture_trace(path: str, *, session_id: int, frame_id: int,
                        sender_capture_uptime_us: int,
                        receiver_decode_monotonic_s: float,
                        receiver_processing_end_monotonic_s: float) -> None:
    if not path:
        raise ValueError("trace path required")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    new_file = not target.exists() or target.stat().st_size == 0
    fd = os.open(str(target), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "session_id": session_id,
            "frame_id": frame_id,
            "sender_capture_uptime_us": sender_capture_uptime_us,
            "receiver_decode_monotonic_s": receiver_decode_monotonic_s,
            "receiver_processing_end_monotonic_s": receiver_processing_end_monotonic_s,
        })
        stream.flush()
