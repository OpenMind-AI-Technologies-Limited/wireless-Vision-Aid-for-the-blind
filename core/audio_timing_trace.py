"""Research-only TTS queue/synthesis timing; not acoustic delivery proof."""
from __future__ import annotations

import csv
import os
from pathlib import Path

FIELDS = (
    "session_id", "frame_id", "sender_capture_tick_us",
    "enqueue_receiver_monotonic_s", "tts_start_monotonic_s",
    "tts_engine_return_monotonic_s",
)


def record_tts_timing(
    path: str, *, session_id: int, frame_id: int,
    sender_capture_tick_us: int | None,
    enqueue_receiver_monotonic_s: float,
    tts_start_monotonic_s: float,
    tts_engine_return_monotonic_s: float,
) -> None:
    if not path:
        raise ValueError("TTS timing output path required")
    if not (enqueue_receiver_monotonic_s <= tts_start_monotonic_s
            <= tts_engine_return_monotonic_s):
        raise ValueError("nonmonotonic TTS event timestamps")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    is_new = not target.exists() or target.stat().st_size == 0
    fd = os.open(str(target), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "a", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(dict(
            session_id=session_id, frame_id=frame_id,
            sender_capture_tick_us=sender_capture_tick_us
            if sender_capture_tick_us is not None else "",
            enqueue_receiver_monotonic_s=enqueue_receiver_monotonic_s,
            tts_start_monotonic_s=tts_start_monotonic_s,
            tts_engine_return_monotonic_s=tts_engine_return_monotonic_s,
        ))
