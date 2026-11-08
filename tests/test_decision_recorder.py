from pathlib import Path
import csv
import pytest

from research.decision_recorder import FIELDNAMES, write_decision


def test_recorder_excludes_unapproved_fields(tmp_path: Path):
    path = tmp_path / "decisions.csv"
    row = {field: "x" for field in FIELDNAMES}
    row["image_bytes"] = "private-image"
    write_decision(str(path), row)
    write_decision(str(path), row)
    with path.open(newline="", encoding="utf-8") as handle:
        result = list(csv.DictReader(handle))
    assert len(result) == 2
    assert "image_bytes" not in result[0]
    assert list(result[0]) == list(FIELDNAMES)
    assert "private-image" not in path.read_text(encoding="utf-8")


def test_recorder_rejects_incomplete_record(tmp_path: Path):
    with pytest.raises(ValueError):
        write_decision(str(tmp_path / "x.csv"), {"frame_number": 1})
