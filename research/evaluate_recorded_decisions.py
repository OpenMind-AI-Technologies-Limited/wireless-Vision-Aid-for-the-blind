"""Evaluate ACTUAL recorded navigation decisions against external frame labels.

Two separate CSV files are deliberately required:
1) runtime decision trace from core.decision_recorder;
2) independently produced labels with run_id, frame_number,
   ground_truth_actionable (0/1).

No fabricated ground truth; rejects missing/duplicate/unmatched labels.
Labels must be created by an independent assessment protocol.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from research.paired_statistics import paired_failure_discordance, wilson_95
from research.cluster_bootstrap import paired_cluster_bootstrap


def _read_csv(path: Path, required: set[str]):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: missing required columns")
        yield from reader


def _binary(v: str) -> bool:
    if v not in ("0", "1"):
        raise ValueError("ground_truth_actionable must be 0 or 1")
    return v == "1"


def evaluate_files(decisions_path: Path, labels_path: Path) -> dict:
    labels = {}
    for row in _read_csv(labels_path, {"run_id", "frame_number", "ground_truth_actionable"}):
        key = (row["run_id"], row["frame_number"])
        if key in labels:
            raise ValueError("duplicate independent label")
        labels[key] = _binary(row["ground_truth_actionable"])

    combined = []
    clustered = []
    used = set()
    for row in _read_csv(decisions_path, {
        "run_id", "frame_number", "existing_navigation_action", "cevg_action",
    }):
        key = (row["run_id"], row["frame_number"])
        if key in used:
            raise ValueError("duplicate decision frame")
        used.add(key)
        if key not in labels:
            raise ValueError(f"missing independent label for {key}")
        if row["cevg_action"] not in ("GUIDE", "ABSTAIN"):
            raise ValueError("CEVG was not enabled for all evaluated frames")
        if row["existing_navigation_action"] not in ("GUIDE", "ABSTAIN"):
            raise ValueError("invalid existing navigation decision")
        combined.append((
            labels[key],
            row["existing_navigation_action"] == "GUIDE",
            row["cevg_action"] == "GUIDE",
        ))
        clustered.append((row["run_id"], *combined[-1]))
    if not combined or used != set(labels):
        raise ValueError("empty or mismatched decision and label sets")

    def summarize(index: int):
        tp = fp = tn = fn = 0
        for truth, original, proposed in combined:
            issued = (original, proposed)[index]
            if truth and issued:
                tp += 1
            elif not truth and issued:
                fp += 1
            elif truth and not issued:
                fn += 1
            else:
                tn += 1
        return {
            "TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "unsupported_issued_fraction": fp / (tp + fp) if tp + fp else None,
            "valid_guidance_recall": tp / (tp + fn) if tp + fn else None,
            "abstention_fraction": (tn + fn) / len(combined),
            "unsupported_issued_wilson95": wilson_95(fp, tp + fp),
            "valid_guidance_recall_wilson95": wilson_95(tp, tp + fn),
        }

    cluster_count = len({record[0] for record in clustered})
    clustered_report = paired_cluster_bootstrap(clustered) if cluster_count >= 2 else None
    return {
        "n": len(combined),
        "independent_run_count": cluster_count,
        "clustered_bootstrap": clustered_report,
        "existing_navigation": summarize(0),
        "cevg": summarize(1),
        "paired_unsupported": paired_failure_discordance(combined),
        "limitations": (
            "Ground truth is externally supplied, not independently audited by "
            "the script. Wilson intervals ignore within-run frame correlation. "
            "Directional action identity and audio delivery are not evaluated."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate_files(args.decisions, args.labels)
    formatted = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(formatted, encoding="utf-8")
    print(formatted, end="")


if __name__ == "__main__":
    main()
