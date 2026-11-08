import csv
from pathlib import Path
import pytest

from research.evaluate_recorded_decisions import evaluate_files


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_real_emitted_decision_pairing(tmp_path: Path):
    decisions = tmp_path / "decisions.csv"
    labels = tmp_path / "labels.csv"
    write(decisions, [
        {"run_id": "r1", "frame_number": "1",
         "existing_navigation_action": "GUIDE", "cevg_action": "GUIDE"},
        {"run_id": "r1", "frame_number": "2",
         "existing_navigation_action": "GUIDE", "cevg_action": "ABSTAIN"},
        {"run_id": "r1", "frame_number": "3",
         "existing_navigation_action": "ABSTAIN", "cevg_action": "ABSTAIN"},
    ])
    write(labels, [
        {"run_id": "r1", "frame_number": "1", "ground_truth_actionable": "1"},
        {"run_id": "r1", "frame_number": "2", "ground_truth_actionable": "0"},
        {"run_id": "r1", "frame_number": "3", "ground_truth_actionable": "1"},
    ])
    result = evaluate_files(decisions, labels)
    assert result["n"] == 3
    assert result["existing_navigation"]["FP"] == 1
    assert result["cevg"]["FP"] == 0
    assert result["cevg"]["FN"] == 1
    assert result["paired_unsupported"]["baseline_only_unsupported"] == 1


def test_missing_label_fails_closed(tmp_path: Path):
    decisions, labels = tmp_path / "d.csv", tmp_path / "l.csv"
    write(decisions, [{"run_id": "r1", "frame_number": "1",
                       "existing_navigation_action": "GUIDE",
                       "cevg_action": "ABSTAIN"}])
    write(labels, [{"run_id": "r1", "frame_number": "2",
                    "ground_truth_actionable": "0"}])
    with pytest.raises(ValueError, match="missing independent label"):
        evaluate_files(decisions, labels)
