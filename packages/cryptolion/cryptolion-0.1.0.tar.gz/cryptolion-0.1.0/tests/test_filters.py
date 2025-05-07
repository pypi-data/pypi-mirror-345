# ===== FILE: tests/test_filters.py =====
import pandas as pd

from core.filters import TrendFilter


def test_trend_filter():
    idx = pd.date_range("2025-01-01", periods=5, freq="min")
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5]}, index=idx)
    mask = TrendFilter(span=3).generate_signals(df)
    assert mask.iloc[-1]
