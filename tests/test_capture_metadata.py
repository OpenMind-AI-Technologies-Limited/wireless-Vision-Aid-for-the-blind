import pytest

from core.capture_metadata import (
    CAPTURE_METADATA,
    decode_capture_metadata,
    encode_capture_metadata,
)


def test_metadata_roundtrip_with_frame_binding():
    raw = encode_capture_metadata(123, 54, 123456789)
    assert len(raw) == CAPTURE_METADATA.size
    assert decode_capture_metadata(raw, expected_session_id=123, expected_frame_id=54) == 123456789


def test_metadata_rejects_wrong_frame_or_session():
    raw = encode_capture_metadata(123, 54, 100)
    with pytest.raises(ValueError, match="mismatch"):
        decode_capture_metadata(raw, expected_session_id=123, expected_frame_id=55)
    with pytest.raises(ValueError, match="mismatch"):
        decode_capture_metadata(raw, expected_session_id=124, expected_frame_id=54)


def test_metadata_rejects_corruption_or_length():
    raw = encode_capture_metadata(123, 54, 100)
    with pytest.raises(ValueError):
        decode_capture_metadata(b"bad", expected_session_id=123, expected_frame_id=54)
    with pytest.raises(ValueError):
        decode_capture_metadata(b"xxxx" + raw[4:], expected_session_id=123, expected_frame_id=54)


def test_sender_ids_are_bounded():
    with pytest.raises(ValueError):
        encode_capture_metadata(0, 0, 0)
    with pytest.raises(ValueError):
        encode_capture_metadata(1, 0xFFFFFFFF, 0)
    with pytest.raises(ValueError):
        encode_capture_metadata(1, 0, -1)
