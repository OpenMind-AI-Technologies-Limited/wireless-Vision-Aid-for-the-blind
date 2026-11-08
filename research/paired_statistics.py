"""Transparent statistics for paired research comparisons (stdlib only)."""
from __future__ import annotations

import math


def wilson_95(successes: int, trials: int) -> tuple[float, float] | None:
    """Wilson score 95% interval for a binomial proportion.

    This assumes independent Bernoulli trials and does not correct for
    correlated video frames. Use clustered-by-run analysis for publication.
    """
    if trials < 0 or not 0 <= successes <= trials:
        raise ValueError("invalid successes/trials")
    if trials == 0:
        return None
    z = 1.959963984540054
    p = successes / trials
    zz = z * z
    den = 1 + zz / trials
    ctr = (p + zz / (2 * trials)) / den
    mar = z * math.sqrt(p * (1 - p) / trials + zz / (4 * trials * trials)) / den
    return max(0.0, ctr - mar), min(1.0, ctr + mar)


def paired_failure_discordance(
    truth_and_decisions: list[tuple[bool, bool, bool]],
) -> dict[str, int]:
    """Count where baseline vs candidate makes an unsupported guidance error.

    Input is (independent_ground_truth_actionable, baseline_guide,
    candidate_guide). An unsupported guidance error occurs only when
    ground truth is false and the policy guides.
    """
    baseline_only = candidate_only = both = neither = 0
    for truth, baseline, candidate in truth_and_decisions:
        b = not truth and baseline
        c = not truth and candidate
        if b and c:
            both += 1
        elif b:
            baseline_only += 1
        elif c:
            candidate_only += 1
        else:
            neither += 1
    return {
        "baseline_only_unsupported": baseline_only,
        "candidate_only_unsupported": candidate_only,
        "both_unsupported": both,
        "neither_unsupported": neither,
    }
