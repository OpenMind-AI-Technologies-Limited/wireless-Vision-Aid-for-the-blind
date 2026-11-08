"""Research-only, privacy-minimal decision recorder.

Records policy decisions and technical metadata, not image/video, object names,
addresses, keys, user names, or ground-truth labels. A run ID and external
annotation file are required for future independently labeled analysis.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

FIELDNAMES = (
    "run_id", "frame_number", "frame_age_s", "max_detection_confidence",
    "localization_fresh", "metric_calibrated", "path_available",
    "existing_navigation_action", "cevg_action", "cevg_reason",
)


def write_decision(path: str, row: dict[str, Any]) -> None:
    target = Path(path)
    if not path:
        raise ValueError("research recorder path required")
    if any(k not in row for k in FIELDNAMES):
        raise ValueError("missing research decision fields")
    # Explicitly limit persisted fields to avoid accidental raw-image metadata.
    target.parent.mkdir(parents=True, exist_ok=True)
    new_file = not target.exists() or target.stat().st_size == 0
    fd = os.open(str(target), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "a", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, extrasaction="ignore")
            if new_file:
                writer.writeheader()
            writer.writerow({k: row[k] for k in FIELDNAMES})
            stream.flush()
    except BaseException:
        raise
