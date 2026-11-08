"""Clustered paired-bootstrap uncertainty for correlated wearable-video frames.

The unit of sampling is a *run*, never an individual video frame. A cluster is
an independently repeated trial, not simply a renamed segment of one video.
All returned intervals are descriptive and need adequate independent runs.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict


def paired_cluster_bootstrap(
    observations: list[tuple[str, bool, bool, bool]],
    *,
    replicates: int = 2000,
    seed: int = 2026,
) -> dict:
    """Rows: (independent_run_id, truth_actionable, legacy_guide, cevg_guide).

    Primary difference is *unsupported guidance per frame* (CEVG - legacy).
    Secondary difference is *valid guidance recall* (CEVG - legacy).
    Avoid per-issued fractions in bootstrap because some resamples issue no cue.
    """
    if not observations:
        raise ValueError("no observations")
    if replicates < 100:
        raise ValueError("at least 100 bootstrap replicates required")
    groups = defaultdict(list)
    for run, truth, legacy, cevg in observations:
        if not run or any(type(v) is not bool for v in (truth, legacy, cevg)):
            raise ValueError("invalid cluster observation")
        groups[run].append((truth, legacy, cevg))
    if len(groups) < 2:
        raise ValueError("at least two independent runs required")
    runs = sorted(groups)
    rng = random.Random(seed)

    def differences(batch):
        n = len(batch)
        positives = sum(t for t, _, _ in batch)
        old_bad = sum((not t) and b for t, b, _ in batch)
        new_bad = sum((not t) and c for t, _, c in batch)
        old_good = sum(t and b for t, b, _ in batch)
        new_good = sum(t and c for t, _, c in batch)
        return (new_bad - old_bad) / n, (
            (new_good - old_good) / positives if positives else None
        )

    point = differences([r for group in groups.values() for r in group])
    samples = [[], []]
    for _ in range(replicates):
        batch = []
        for _ in runs:
            batch.extend(groups[runs[rng.randrange(len(runs))]])
        result = differences(batch)
        for i, v in enumerate(result):
            if v is not None:
                samples[i].append(v)

    def interval(values):
        if len(values) < int(0.8 * replicates):
            return None
        values.sort()
        return [
            values[int((len(values) - 1) * 0.025)],
            values[int((len(values) - 1) * 0.975)],
        ]

    return {
        "independent_run_count": len(runs),
        "observations": len(observations),
        "seed": seed,
        "replicates": replicates,
        "delta_unsupported_per_frame": point[0],
        "delta_unsupported_per_frame_ci95": interval(samples[0]),
        "delta_valid_guidance_recall": point[1],
        "delta_valid_guidance_recall_ci95": interval(samples[1]),
        "interpretation": "Negative unsupported delta is favorable; positive recall delta is favorable. Resampling is at independent-run level.",
    }
