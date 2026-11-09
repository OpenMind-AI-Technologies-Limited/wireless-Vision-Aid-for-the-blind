import csv
from core.udp_capture_trace import write_capture_trace


def test_research_capture_trace_contains_no_secrets(tmp_path):
    target = tmp_path / "capture.csv"
    write_capture_trace(
        str(target),
        session_id=5, frame_id=2,
        sender_capture_uptime_us=1234,
        receiver_decode_monotonic_s=10.1,
        receiver_processing_end_monotonic_s=10.2,
    )
    with target.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["sender_capture_uptime_us"] == "1234"
    assert "token" not in target.read_text().lower()
    assert "key" not in target.read_text().lower()
