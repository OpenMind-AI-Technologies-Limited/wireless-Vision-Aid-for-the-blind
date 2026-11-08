import pytest

from core.clock_offset_bounds import FourTimestampExchange, infer_offset_interval


def sample():
    # Receiver minus sender clock offset = 5s, 20ms each network direction.
    return FourTimestampExchange(
        receiver_request_s=15.0,
        sender_received_s=10.02,
        sender_replied_s=10.03,
        receiver_reply_received_s=15.05,
        authenticated_exchange=True,
        same_nonce_and_session=True,
    )


def test_four_timestamp_bounds_include_true_offset():
    interval = infer_offset_interval(sample())
    assert interval.lower_s <= 5 <= interval.upper_s
    assert interval.width_s == pytest.approx(0.04)


def test_unauthenticated_or_replayed_exchange_rejected():
    from dataclasses import replace
    with pytest.raises(ValueError):
        infer_offset_interval(replace(sample(), authenticated_exchange=False))
    with pytest.raises(ValueError):
        infer_offset_interval(replace(sample(), same_nonce_and_session=False))


def test_large_network_delay_rejected():
    from dataclasses import replace
    with pytest.raises(ValueError, match="uncertainty"):
        infer_offset_interval(replace(sample(), receiver_reply_received_s=15.5))


def test_invalid_monotonic_sender_timestamps():
    from dataclasses import replace
    with pytest.raises(ValueError, match="nonmonotonic"):
        infer_offset_interval(replace(sample(), sender_replied_s=10.01))
