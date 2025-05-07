import numpy as np
import pandas as pd
import pytest

from core.entries import DonchianEntry, EMACrossEntry, MACDEntry, RSIEntry


@pytest.fixture
def simple_df():
    # prices that first rise then fall then cross back up
    prices = pd.Series([1, 2, 3, 2, 4, 5])
    highs = prices + 0.5
    lows = prices - 0.5
    return pd.DataFrame({"close": prices, "high": highs, "low": lows})


def test_ema_cross_entry(simple_df):
    sig = EMACrossEntry(short=2, long=3).generate_signals(simple_df)
    # Expect at least one True
    assert sig.any()
    # First non-zero must occur when short EMA crosses above long EMA
    idx = sig[sig].index[0]
    assert idx > 0


def test_macd_entry(simple_df):
    sig = MACDEntry(fast=2, slow=4, signal=2).generate_signals(simple_df)
    assert isinstance(sig, pd.Series)


def test_donchian_entry(simple_df):
    sig = DonchianEntry(period=3).generate_signals(simple_df)
    # you should break above the high of the previous 3
    assert sig.iloc[-1] == True


def test_rsi_entry(simple_df):
    sig = RSIEntry(period=3, threshold=50).generate_signals(simple_df)
    assert isinstance(sig, pd.Series)
