# ===== FILE: tests/test_filters_extended.py =====
import pandas as pd
import pytest

from core.filters import ADXFilter, VolumeSpikeFilter


@pytest.fixture
def sample_df():
    idx = pd.date_range("2025-01-01", periods=6, freq="min")
    df = pd.DataFrame(
        {
            "close": [1, 2, 3, 4, 5, 6],
            "high": [1.1, 2.1, 3.1, 4.1, 5.1, 6.1],
            "low": [0.9, 1.9, 2.9, 3.9, 4.9, 5.9],
            "volume": [100, 150, 300, 250, 400, 350],
        },
        index=idx,
    )
    return df


def test_volume_spike_filter(sample_df):
    mask = VolumeSpikeFilter(threshold=2.0, window=2).generate_signals(sample_df)
    assert mask.dtype == bool and mask.any()


def test_adx_filter_constant(sample_df):
    df = sample_df.copy()
    df["close"] = 100
    mask = ADXFilter(length=3, threshold=20).generate_signals(df)
    assert not mask.any()
