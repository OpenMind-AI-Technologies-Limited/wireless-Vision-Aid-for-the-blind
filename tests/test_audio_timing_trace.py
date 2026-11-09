import csv
import pytest

from core.audio_timing_trace import record_tts_timing


def test_tts_timing_records_frame_binding_without_transcript(tmp_path):
    out = tmp_path / "tts.csv"
    record_tts_timing(str(out), session_id=1, frame_id=3,
                      sender_capture_tick_us=234000,
                      enqueue_receiver_monotonic_s=10.0,
                      tts_start_monotonic_s=10.2,
                      tts_engine_return_monotonic_s=10.7)
    with out.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["frame_id"] == "3"
    assert rows[0]["sender_capture_tick_us"] == "234000"
    assert "transcript" not in rows[0]
    assert "text" not in rows[0]


def test_invalid_order_rejected(tmp_path):
    with pytest.raises(ValueError):
        record_tts_timing(str(tmp_path / "bad.csv"),
                          session_id=1, frame_id=2,
                          sender_capture_tick_us=None,
                          enqueue_receiver_monotonic_s=1.0,
                          tts_start_monotonic_s=2.0,
                          tts_engine_return_monotonic_s=1.9)
