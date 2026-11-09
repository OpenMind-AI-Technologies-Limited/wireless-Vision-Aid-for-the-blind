"""Authenticated clock challenge/response simulated on the actual receiver class.

These validate protocol state and cryptography in software only; no radio,
ESP32 board timing or accessibility outcomes are tested here.
"""
import os
import time
from Crypto.Cipher import AES

from core.udp_protocol import (
    AUTH_FRAME_ID, HEADER_SIZE, NONCE_SIZE, TAG_SIZE, pack_header, unpack_header,
)
from core.udp_clock_wire import decode_request, encode_response
from core.evidence_gate import GateConfig
from core.udp_runtime import UDPVisionServer

KEY = bytes(range(32))
ADDR = ("192.168.4.2", 9999)
SESSION = 509


class FakeSocket:
    def __init__(self):
        self.packets = []

    def sendto(self, payload, addr):
        self.packets.append((payload, addr))
        return len(payload)


def receiver():
    server = UDPVisionServer.__new__(UDPVisionServer)
    server.remote_cevg_enabled = True
    server.encrypt_udp = True
    server.require_auth = True
    server.auth_ttl_s = 120.0
    server.udp_key = KEY
    server.AES = AES
    server.get_random_bytes = os.urandom
    server.sock = FakeSocket()
    server.sync_pending = {}
    server.sync_exchanges = {}
    server.sync_last_request = {}
    server.sessions = {
        ADDR: {
            "session_id": SESSION,
            "authenticated_at": time.monotonic(),
            "last_seen": time.monotonic(),
        }
    }
    server.remote_cevg_config = GateConfig(max_age_s=0.5, min_confidence=0.5)
    server.remote_cevg_last_reason = ""
    return server


def authenticated_response(server, *, alter_challenge=False, alter_tag=False):
    request_packet, address = server.sock.packets[-1]
    assert address == ADDR
    request_header = request_packet[:HEADER_SIZE]
    sid, frame, total, index, sz = unpack_header(request_header)
    assert (sid, frame, total, index) == (SESSION, AUTH_FRAME_ID, 0, 1)
    nonce = request_packet[HEADER_SIZE:HEADER_SIZE + NONCE_SIZE]
    tag = request_packet[HEADER_SIZE + NONCE_SIZE:HEADER_SIZE + NONCE_SIZE + TAG_SIZE]
    ciphertext = request_packet[HEADER_SIZE + NONCE_SIZE + TAG_SIZE:]
    decoder = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    decoder.update(request_header)
    challenge, r1 = decode_request(decoder.decrypt_and_verify(ciphertext, tag))
    if alter_challenge:
        challenge = bytes([challenge[0] ^ 1]) + challenge[1:]

    s2 = r1 - 5_000_000
    s3 = s2
    response_clear = encode_response(challenge, r1, s2, s3)
    response_header = pack_header(
        SESSION, AUTH_FRAME_ID, 0, 2, NONCE_SIZE + TAG_SIZE + len(response_clear)
    )
    response_nonce = os.urandom(12)
    encoder = AES.new(KEY, AES.MODE_GCM, nonce=response_nonce)
    encoder.update(response_header)
    encrypted, response_tag = encoder.encrypt_and_digest(response_clear)
    if alter_tag:
        response_tag = bytes([response_tag[0] ^ 1]) + response_tag[1:]
    arrival_us = time.monotonic_ns() // 1000
    return response_header, response_nonce + response_tag + encrypted, arrival_us


def test_nonce_bound_authenticated_exchange_releases_fresh_warning():
    server = receiver()
    assert server._send_clock_challenge(ADDR, SESSION)
    header, payload, arrival = authenticated_response(server)
    assert server._handle_clock_response(ADDR, SESSION, header, payload, arrival)
    assert not server._handle_clock_response(ADDR, SESSION, header, payload, arrival)
    capture_tick = time.monotonic_ns() // 1000 - 5_000_000 - 20_000
    assert server._evaluate_remote_warning(ADDR, SESSION, 5, capture_tick, 0.9)
    assert server.remote_cevg_last_reason == "fresh_authenticated_obstacle_warning"


def test_forged_response_tag_never_creates_clock_proof():
    server = receiver()
    server._send_clock_challenge(ADDR, SESSION)
    header, payload, arrival = authenticated_response(server, alter_tag=True)
    assert not server._handle_clock_response(ADDR, SESSION, header, payload, arrival)
    assert server.sync_exchanges == {}


def test_wrong_challenge_cannot_authorize_frame():
    server = receiver()
    server._send_clock_challenge(ADDR, SESSION)
    header, payload, arrival = authenticated_response(server, alter_challenge=True)
    assert not server._handle_clock_response(ADDR, SESSION, header, payload, arrival)
    assert not server._evaluate_remote_warning(ADDR, SESSION, 5, 1000, 0.9)


def test_unavailable_sync_never_releases_audio():
    server = receiver()
    assert not server._evaluate_remote_warning(ADDR, SESSION, 5, 12345, 0.9)
    assert server.remote_cevg_last_reason == "missing_verified_remote_capture_proof"
