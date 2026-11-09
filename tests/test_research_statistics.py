import pytest

from research.paired_statistics import paired_failure_discordance, wilson_95


def test_wilson_interval_extremes():
    assert wilson_95(0, 0) is None
    low, high = wilson_95(0, 100)
    assert low == 0
    assert 0 < high < 0.05
    low, high = wilson_95(100, 100)
    assert 0.95 < low < 1
    assert high == 1


def test_wilson_rejects_impossible_counts():
    with pytest.raises(ValueError):
        wilson_95(11, 10)


def test_paired_failure_discordance():
    rows = [(False, True, False), (False, False, True),
            (False, True, True), (True, True, False)]
    result = paired_failure_discordance(rows)
    assert result == {
        "baseline_only_unsupported": 1,
        "candidate_only_unsupported": 1,
        "both_unsupported": 1,
        "neither_unsupported": 1,
    }
