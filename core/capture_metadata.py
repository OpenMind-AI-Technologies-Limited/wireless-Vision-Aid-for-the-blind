"""Research-only versioned camera-capture metadata codec.

This codec MUST be serialized inside authenticated-encrypted frame content or
included as authenticated AAD. Its binary structure alone is not integrity
protection. Not yet used by the production ESP32-CAM UDP wire protocol.
"""
from __future__ import annotations

import struct

MAGIC = b"WVC3"
VERSION = 1
CAPTURE_METADATA = struct.Struct("!4sBIIQ")
MAX_TICK_US = (1 << 64) - 1


def encode_capture_metadata(session_id: int, frame_id: int, tick_us: int) -> bytes:
    """Encode authenticated-data candidate with sender monotonic capture tick."""
    if not 1 <= session_id <= 0xFFFFFFFF:
        raise ValueError("invalid sender session")
    if not 0 <= frame_id <= 0xFFFFFFFE:
        raise ValueError("invalid data-frame ID")
    if not 0 <= tick_us <= MAX_TICK_US:
        raise ValueError("invalid monotonic capture tick")
    return CAPTURE_METADATA.pack(MAGIC, VERSION, session_id, frame_id, tick_us)


def decode_capture_metadata(
    raw: bytes, *, expected_session_id: int, expected_frame_id: int
) -> int:
    """Decode only after verifying enclosing AEAD tag and sender session.

    Returns untrusted sender tick value until verified clock mapping is supplied.
    """
    if len(raw) != CAPTURE_METADATA.size:
        raise ValueError("invalid capture metadata length")
    magic, version, session_id, frame_id, tick_us = CAPTURE_METADATA.unpack(raw)
    if magic != MAGIC or version != VERSION:
        raise ValueError("unsupported capture metadata")
    if session_id != expected_session_id or frame_id != expected_frame_id:
        raise ValueError("capture metadata session/frame mismatch")
    return tick_us


def extract_capture_envelope(
    plaintext: bytes, *, expected_session_id: int, expected_frame_id: int
) -> tuple[int, bytes]:
    """Extract V3 sender uptime and image from already AEAD-verified frame.

    Caller must authenticate every chunk of the assembled frame before calling
    this function. Sender uptime is not receiver clock time.
    """
    if len(plaintext) <= CAPTURE_METADATA.size:
        raise ValueError("capture envelope does not contain image bytes")
    capture_tick_us = decode_capture_metadata(
        plaintext[:CAPTURE_METADATA.size],
        expected_session_id=expected_session_id,
        expected_frame_id=expected_frame_id,
    )
    return capture_tick_us, plaintext[CAPTURE_METADATA.size:]
