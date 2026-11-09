"""Independent dynamic-scene research simulation (NOT physical-user testing).

Warning truth uses object position at output time, independently of the
confidence, authentication and freshness policy. Simulated source-side
buffering is deliberately invisible to receiver-arrival timestamps.
"""
import argparse
import csv
import random
import statistics
from pathlib import Path

from core.evidence_gate import GateConfig
from core.remote_capture_proof import CaptureProof
from core.remote_guidance_release import release_remote_obstacle_warning


def bearing(x):
    if x < -0.45:
        return "left"
    if x > 0.45:
        return "right"
    return "center"


def simulate(seed, n, scenario, max_age=0.5, score_threshold=0.5):
    rng = random.Random(seed)
    names = ("confidence", "receiver_fresh", "capture_bound")
    counts = {p: dict(tp=0, fp=0, tn=0, fn=0) for p in names}
    for _ in range(n):
        present = rng.random() < 0.77
        detected = rng.random() < (0.91 if present else 0.13)
        confidence = (
            rng.betavariate(6.8, 2.3) if present else rng.betavariate(3.5, 5.2)
        ) if detected else 0
        capture_x = rng.uniform(-1.75, 1.75)
        velocity = rng.uniform(-1.5, 1.5)
        sensor_noise = rng.gauss(0, 0.12)
        announced_direction = bearing(capture_x + sensor_noise)
        if scenario == "nominal":
            upstream_delay = rng.uniform(0.012, 0.14)
        elif scenario == "burst":
            upstream_delay = (rng.uniform(0.48, 1.8) if rng.random() < 0.55
                              else rng.uniform(0.01, 0.14))
        elif scenario == "mixed":
            upstream_delay = (rng.uniform(0.48, 1.8) if rng.random() < 0.3
                              else rng.uniform(0.01, 0.14))
        else:
            raise ValueError(scenario)
        processing_delay = rng.uniform(0.025, 0.18)
        true_age = upstream_delay + processing_delay
        decision_x = capture_x + velocity * true_age
        supported = bool(
            present and detected and abs(decision_x) <= 1.75
            and bearing(decision_x) == announced_direction
        )
        verified_clock = rng.random() < 0.965
        clock_bound_error = rng.uniform(0.002, 0.055)
        # Exercise the ACTUAL experimental warning-release implementation.
        # Synthetic clock offset is zero; its verified lower bound is negative
        # by the independently drawn uncertainty interval.
        capture_proof = CaptureProof(
            sender_capture_s=100.0,
            receiver_decision_s=100.0 + true_age,
            offset_lower_s=-clock_bound_error,
            offset_upper_s=0.0,
            trusted_clock_mapping=True,
            authenticated_frame=True,
            matched_session_and_frame=True,
        ) if verified_clock else None
        proposed_issued = release_remote_obstacle_warning(
            capture_proof,
            confidence=confidence,
            config=GateConfig(max_age_s=max_age, min_confidence=score_threshold),
        ).action == "GUIDE"
        predicted = {
            "confidence": detected and confidence >= score_threshold,
            "receiver_fresh": (
                detected and confidence >= score_threshold
                and processing_delay <= max_age
            ),
            "capture_bound": bool(detected and proposed_issued),
        }
        for key in names:
            issued = predicted[key]
            cls = ("tp" if supported else "fp") if issued else (
                "fn" if supported else "tn"
            )
            counts[key][cls] += 1
    result = []
    for name in names:
        c = counts[name]
        issued = c["tp"] + c["fp"]
        truth = c["tp"] + c["fn"]
        result.append(dict(
            seed=seed, scenario=scenario, policy=name, n=n, **c,
            unsupported_per_issued=c["fp"] / issued if issued else None,
            valid_warning_recall=c["tp"] / truth if truth else None,
            abstention=(c["tn"] + c["fn"]) / n,
            unsupported_per_frame=c["fp"] / n,
        ))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--frames", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument("--out", type=Path, default=Path("independent_simulation_results.csv"))
    args = parser.parse_args()
    if args.runs < 2 or args.frames < 1:
        raise ValueError("runs >=2 and frames >=1 required")
    rows = []
    offsets = {"nominal": 0, "mixed": 100000, "burst": 200000}
    for scenario in ("nominal", "mixed", "burst"):
        for index in range(args.runs):
            rows.extend(simulate(
                args.seed + index * 337 + offsets[scenario],
                args.frames, scenario,
            ))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for scenario in ("nominal", "mixed", "burst"):
        print(scenario)
        for policy in ("confidence", "receiver_fresh", "capture_bound"):
            group = [r for r in rows if r["scenario"] == scenario and r["policy"] == policy]
            print(policy, *(f"{field}={statistics.mean(r[field] for r in group):.5f}"
                            for field in ("unsupported_per_issued", "valid_warning_recall",
                                          "abstention", "unsupported_per_frame")))
    print("run-level data:", args.out)


if __name__ == "__main__":
    main()
