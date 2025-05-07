# ===== FILE: tests/test_exits.py =====
import pandas as pd
import pytest

from core.exits import (ATRStopExit, ChandelierExit, ProfitTargetExit, RSIExit,
                        TimeExit)


@pytest.fixture
def price_df():
    # 10 bars of flat price 100
    idx = pd.date_range("2025-01-01", periods=10, freq="min")
    return pd.DataFrame({"open": 100, "high": 100, "low": 100, "close": 100}, index=idx)


def test_time_exit(price_df):
    pos = pd.Series(0, index=price_df.index)
    mask = TimeExit(max_bars=5).generate_exits(price_df, pos)
    assert not mask.any()


def test_profit_target_exit(price_df):
    pos = pd.Series([0] * 3 + [1] * 7, index=price_df.index)
    price_df.loc[price_df.index[-1], "close"] = 102
    mask = ProfitTargetExit(target=0.01).generate_exits(price_df, pos)
    assert mask.iloc[-1]
