# ===== FILE: tests/test_sizing.py =====
import numpy as np
import pandas as pd

from core.sizing import ATRUnitSizer, FixedPctSizer, KellySizer


def make_df():
    idx = pd.date_range("2025-01-01", periods=10, freq="min")
    return pd.DataFrame({"close": np.linspace(100, 110, 10)}, index=idx)


def test_fixed_pct_sizer():
    df = make_df()
    sig = pd.Series(1, index=df.index)
    sizes = FixedPctSizer(0.1).size_positions(df, sig)
    assert (sizes == 0.1).all()


def test_kelly_sizer_small_data():
    df = make_df()
    sig = pd.Series(1, index=df.index)
    sizes = KellySizer(lookback=5, rf=0).size_positions(df, sig)
    assert not sizes.isna().any() and (sizes <= 1).all()


def test_atr_unit_sizer():
    df = make_df().assign(high=lambda d: d.close + 1, low=lambda d: d.close - 1)
    sig = pd.Series(1, index=df.index)
    sizes = ATRUnitSizer(length=3, unit_size=2).size_positions(df, sig)
    assert not sizes.isna().any()
