import pandas as pd
import numpy as np
import pytest
from core.strategy import StrategyEngine

def make_df():
    idx = pd.date_range("2025-01-01", periods=6, freq="min")
    # step by 5 so entry@105, exit@110 produce profit=5
    base = 100 + 5 * np.arange(len(idx))
    return pd.DataFrame(
        {
            "open":  base,
            "high":  base + 1,
            "low":   base - 1,
            "close": base,
        },
        index=idx,
    )

def test_overlapping_entries_exits():
    df = make_df()
    entries = pd.Series([1, 1, 0, 0, 0, 0], index=df.index).astype(bool)
    exits   = pd.Series([0, 0, 1, 0, 0, 0], index=df.index).astype(bool)
    sizes   = pd.Series(1.0, index=df.index)
    eq = StrategyEngine(100).run(df, entries=entries, exits=exits, sizes=sizes)
    # Only first entry should be respected → profit = 110 - 105 = 5
    assert eq.iloc[-1] == pytest.approx(105)

def test_zero_size_ignored():
    df = make_df()
    entries = pd.Series([1, 0, 0, 0, 0, 0], index=df.index).astype(bool)
    exits   = pd.Series(False, index=df.index)
    sizes   = pd.Series([0, 0, 0, 0, 0, 0], index=df.index)  # zero size
    eq = StrategyEngine(100).run(df, entries=entries, exits=exits, sizes=sizes)
    assert (eq == 100).all()  # no trade executed

def test_fractional_sizes():
    df = make_df()
    entries = pd.Series([1, 0, 0, 0, 0, 0], index=df.index).astype(bool)
    exits   = pd.Series([0, 0, 1, 0, 0, 0], index=df.index).astype(bool)
    sizes   = pd.Series([0.5, 0, 0.5, 0, 0, 0], index=df.index)
    eq = StrategyEngine(100).run(df, entries=entries, exits=exits, sizes=sizes)
    # half position → profit = 0.5 * (110 - 100) = 5
    assert eq.iloc[2] == pytest.approx(105)
