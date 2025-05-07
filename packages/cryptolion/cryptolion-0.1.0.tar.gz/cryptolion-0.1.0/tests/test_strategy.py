import pandas as pd
import pytest

from core.strategy import StrategyEngine  # ← use the actual class name


@pytest.fixture
def empty_df():
    # supply an empty DataFrame with at least the OHLC columns
    return pd.DataFrame([], columns=["open", "high", "low", "close"], index=[])


def test_engine_no_signals(empty_df):
    engine = StrategyEngine()
    equity = engine.run(empty_df, signals=pd.Series(0, index=empty_df.index))
    # with no signals, equity should stay at starting_cash
    assert equity.iloc[0] == engine.starting_cash
