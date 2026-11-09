import csv
import pytest
from core.sync_interval_trace import write_sync_interval


def test_records_clock_bounds_without_keys_or_challenges(tmp_path):
    path = tmp_path / "sync.csv"
    write_sync_interval(
        str(path), session_id=10,
        receiver_reply_received_monotonic_s=100.0,
        receiver_minus_sender_offset_lower_s=5.01,
        receiver_minus_sender_offset_upper_s=5.03,
    )
    with path.open(newline="", encoding="utf-8") as handle:
        result = list(csv.DictReader(handle))
    assert len(result) == 1
    assert float(result[0]["offset_interval_width_s"]) == pytest.approx(0.02)
    assert "nonce" not in result[0]


def test_rejects_impossible_offset_interval(tmp_path):
    with pytest.raises(ValueError):
        write_sync_interval(str(tmp_path / "x.csv"), session_id=1,
                            receiver_reply_received_monotonic_s=2,
                            receiver_minus_sender_offset_lower_s=3,
                            receiver_minus_sender_offset_upper_s=2)
