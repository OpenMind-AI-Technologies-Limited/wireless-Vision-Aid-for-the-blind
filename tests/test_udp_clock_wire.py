import pytest
from core.udp_clock_wire import (
    encode_request, decode_request, encode_response, decode_response,
    REQUEST_PLAIN_SIZE, RESPONSE_PLAIN_SIZE,
)


def test_roundtrip():
    nonce = bytes(range(16))
    request = encode_request(nonce, 123456)
    assert len(request) == REQUEST_PLAIN_SIZE
    assert decode_request(request) == (nonce, 123456)
    response = encode_response(nonce, 123456, 120000, 120015)
    assert len(response) == RESPONSE_PLAIN_SIZE
    assert decode_response(response) == (nonce, 123456, 120000, 120015)


def test_request_rejects_malformed_data():
    with pytest.raises(ValueError):
        encode_request(b"x", 12)
    with pytest.raises(ValueError):
        decode_request(b"bad")
    with pytest.raises(ValueError):
        decode_request(bytes([2])+encode_request(b"x"*16, 0)[1:])


def test_response_rejects_nonmonotonic_or_bad_version():
    nonce = b"0"*16
    with pytest.raises(ValueError):
        encode_response(nonce, 1, 5, 4)
    with pytest.raises(ValueError):
        decode_response(b"bad")
    data = encode_response(nonce, 1, 5, 7)
    with pytest.raises(ValueError):
        decode_response(bytes([3])+data[1:])
