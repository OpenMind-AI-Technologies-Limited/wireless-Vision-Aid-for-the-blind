"""Replay labeled observation traces through baseline and experimental guidance policies.

CSV schema:
observed_at_monotonic,evaluated_at_monotonic,confidence,origin,authenticated,
localization_fresh,metric_calibrated,path_available,ground_truth_actionable

ground_truth_actionable MUST be independently labeled, not constructed from
the CEVG gates. This executable compares decisions; it does not infer safety
benefit from synthetic scenarios.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from core.evidence_gate import Evidence, GateConfig, evaluate

FIELDS = (
    "observed_at_monotonic", "evaluated_at_monotonic", "confidence",
    "origin", "authenticated", "localization_fresh",
    "metric_calibrated", "path_available", "ground_truth_actionable",
)


def as_bool(value: str) -> bool:
    if str(value).strip().lower() in ("true", "1", "yes"):
        return True
    if str(value).strip().lower() in ("false", "0", "no"):
        return False
    raise ValueError(f"invalid boolean: {value!r}")


def load_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or any(x not in reader.fieldnames for x in FIELDS):
            raise ValueError("trace missing required fields")
        for row in reader:
            evidence = Evidence(
                observed_at_monotonic=float(row["observed_at_monotonic"]),
                evaluated_at_monotonic=float(row["evaluated_at_monotonic"]),
                confidence=float(row["confidence"]),
                origin=row["origin"],
                authenticated=as_bool(row["authenticated"]),
                localization_fresh=as_bool(row["localization_fresh"]),
                metric_calibrated=as_bool(row["metric_calibrated"]),
                path_available=as_bool(row["path_available"]),
            )
            yield evidence, as_bool(row["ground_truth_actionable"])


def decide_baseline(name: str, evidence: Evidence, cfg: GateConfig) -> bool:
    confidence_ok = evidence.confidence >= cfg.min_confidence
    if name == "confidence":
        return confidence_ok
    if name == "auth_confidence":
        return confidence_ok and (
            evidence.origin == "local" or (
                evidence.origin == "remote" and evidence.authenticated
            )
        )
    if name == "freshness_confidence":
        age = evidence.evaluated_at_monotonic - evidence.observed_at_monotonic
        return confidence_ok and 0 <= age <= cfg.max_age_s
    if name == "cevg":
        return evaluate(evidence, cfg).action == "GUIDE"
    raise ValueError(name)


def metrics(rows, cfg: GateConfig):
    observations = list(rows)
    if not observations:
        raise ValueError("empty trace")
    output = {}
    for name in ("confidence", "auth_confidence", "freshness_confidence", "cevg"):
        tp = fp = tn = fn = 0
        for evidence, truth in observations:
            predicted = decide_baseline(name, evidence, cfg)
            if predicted and truth:
                tp += 1
            elif predicted and not truth:
                fp += 1
            elif not predicted and truth:
                fn += 1
            else:
                tn += 1
        total = tp + fp + tn + fn
        output[name] = {
            "n": total,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "unsupported_issued_fraction": fp / (tp + fp) if tp + fp else None,
            "valid_guidance_recall": tp / (tp + fn) if tp + fn else None,
            "abstention_fraction": (tn + fn) / total,
        }
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--max-age-s", type=float, default=0.5)
    parser.add_argument("--min-confidence", type=float, default=0.5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = {
        "evidence": "externally_labeled_trace_not_automatically_verified",
        "source_file": str(args.trace),
        "policies": metrics(
            load_rows(args.trace),
            GateConfig(max_age_s=args.max_age_s, min_confidence=args.min_confidence),
        ),
    }
    content = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.write_text(content, encoding="utf-8")
    print(content, end="")


if __name__ == "__main__":
    main()
