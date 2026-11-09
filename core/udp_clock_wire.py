"""Experimental authenticated UDP clock exchange payloads.

Control packets reuse AUTH_FRAME_ID with total_chunks=0 and chunk_index
1=request, 2=response. They MUST be AES-GCM authenticated with the 14-byte
header as AAD; this module alone does not perform authentication.
"""
from __future__ import annotations

import struct

REQUEST_CHUNK_INDEX = 1
RESPONSE_CHUNK_INDEX = 2
SYNC_VERSION = 1
SYNC_CHALLENGE_SIZE = 16
_REQUEST = struct.Struct("!B16sQ")
_RESPONSE = struct.Struct("!B16sQQQ")
REQUEST_PLAIN_SIZE = _REQUEST.size
RESPONSE_PLAIN_SIZE = _RESPONSE.size


def encode_request(challenge: bytes, receiver_sent_us: int) -> bytes:
    if len(challenge) != SYNC_CHALLENGE_SIZE or not 0 <= receiver_sent_us < 1 << 64:
        raise ValueError("invalid sync request")
    return _REQUEST.pack(SYNC_VERSION, challenge, receiver_sent_us)


def decode_request(data: bytes) -> tuple[bytes, int]:
    if len(data) != _REQUEST.size:
        raise ValueError("invalid sync request size")
    version, challenge, r1 = _REQUEST.unpack(data)
    if version != SYNC_VERSION:
        raise ValueError("invalid sync version")
    return challenge, r1


def encode_response(challenge: bytes, receiver_sent_us: int,
                    sender_received_us: int, sender_replied_us: int) -> bytes:
    if len(challenge) != SYNC_CHALLENGE_SIZE:
        raise ValueError("invalid challenge")
    if not all(0 <= x < 1 << 64 for x in
               (receiver_sent_us, sender_received_us, sender_replied_us)):
        raise ValueError("invalid sync timestamps")
    if sender_replied_us < sender_received_us:
        raise ValueError("nonmonotonic sender timestamps")
    return _RESPONSE.pack(SYNC_VERSION, challenge, receiver_sent_us,
                          sender_received_us, sender_replied_us)


def decode_response(data: bytes) -> tuple[bytes, int, int, int]:
    if len(data) != _RESPONSE.size:
        raise ValueError("invalid sync response size")
    version, challenge, r1, s2, s3 = _RESPONSE.unpack(data)
    if version != SYNC_VERSION or s3 < s2:
        raise ValueError("invalid sync response")
    return challenge, r1, s2, s3
