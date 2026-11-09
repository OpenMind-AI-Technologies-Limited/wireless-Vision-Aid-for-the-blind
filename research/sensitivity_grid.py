"""Research-only sensitivity sweep, no physical-device measurements."""
import argparse
import csv
import statistics
from pathlib import Path
from research.independent_scene_simulation import simulate


def sweep(runs=10, frames=1000):
    if runs < 2 or frames < 1:
        raise ValueError("requires at least 2 independent runs and 1 frame")
    rows = []
    offsets = {"nominal": 0, "mixed": 100000, "burst": 200000}
    for scenario in ("nominal", "mixed", "burst"):
        for max_age in (0.25, 0.5, 0.75, 1.0):
            for threshold in (0.4, 0.5, 0.6):
                cases = []
                for index in range(runs):
                    cases.extend(simulate(
                        7001 + index * 337 + offsets[scenario],
                        frames, scenario,
                        max_age=max_age, score_threshold=threshold,
                    ))
                for policy in ("receiver_fresh", "capture_bound"):
                    group = [r for r in cases if r["policy"] == policy]
                    rows.append({
                        "scenario": scenario,
                        "max_age_s": max_age,
                        "min_confidence": threshold,
                        "policy": policy,
                        "unsupported_per_issued": statistics.mean(
                            r["unsupported_per_issued"] for r in group
                        ),
                        "valid_warning_recall": statistics.mean(
                            r["valid_warning_recall"] for r in group
                        ),
                        "abstention": statistics.mean(
                            r["abstention"] for r in group
                        ),
                    })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--frames", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=Path("sensitivity_results.csv"))
    args = parser.parse_args()
    rows = sweep(args.runs, args.frames)
    with args.out.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} synthetic sensitivity settings written to {args.out}")


if __name__ == "__main__":
    main()
