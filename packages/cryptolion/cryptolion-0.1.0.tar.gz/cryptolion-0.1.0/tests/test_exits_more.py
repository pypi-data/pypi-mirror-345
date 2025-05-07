# ===== FILE: tests/test_exits_more.py =====
import numpy as np
import pandas as pd
import pytest

from core.exits import ATRStopExit as ATRWrapper
from core.exits import ChandelierExit, RSIExit
from core.exits_atr import ATRStopExit


@pytest.fixture
def df():
    idx = pd.date_range("2025-01-01", periods=20, freq="min")
    base = pd.Series(np.linspace(100, 110, len(idx)), index=idx)
    return pd.DataFrame(
        {"open": base, "high": base + 1, "low": base - 1, "close": base}, index=idx
    )


def test_chandelier_exit(df):
    pos = pd.Series(1, index=df.index)
    df2 = df.copy()
    df2.loc[df2.index[-1], "close"] = df2["high"].iloc[-5] - 5
    mask = ChandelierExit(lookback=5, atr_length=5, multiplier=1.0).generate_exits(
        df2, pos
    )
    assert mask.iloc[-1]


def test_rsi_exit(df):
    pos = pd.Series(1, index=df.index)
    df2 = df.copy()
    # ramp up then drop to force RSI cross
    df2["close"] = list(np.linspace(100, 150, 5)) + [150] * 15
    df2.loc[df2.index[-1], "close"] = 50
    mask = RSIExit(length=3, threshold=50).generate_exits(df2, pos)
    assert mask.iloc[-1]


def test_atr_wrapper(df):
    pos = pd.Series(1, index=df.index)
    df2 = df.copy()
    df2.loc[df2.index[-1], "close"] = df2["close"].iloc[-2] - 5
    mask1 = ATRStopExit(length=5, multiplier=1.0).generate_exits(df2, pos)
    mask2 = ATRWrapper(length=5, multiplier=1.0).generate_exits(df2, pos)
    assert mask1.iloc[-1] and mask2.iloc[-1]
