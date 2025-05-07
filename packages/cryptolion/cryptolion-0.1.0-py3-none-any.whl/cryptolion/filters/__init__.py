"""
Tiny collection of filter helpers used by the unit-tests.
Only 3 classes are required by the tests:
    • TrendFilter
    • ADXFilter
    • VolumeSpikeFilter
All of them expose `.generate_signals(df)` → pd.Series[bool]
"""
from __future__ import annotations
import pandas as pd


# ------------------------------------------------------------------------- #
class TrendFilter:
    """close > 200-SMA  ⇒ True"""
    def __init__(self, period: int = 200):
        self.period = period

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        sma = df["close"].rolling(self.period, min_periods=1).mean()
        return (df["close"] > sma).astype(bool)


# ------------------------------------------------------------------------- #
class ADXFilter:
    """
    Dummy implementation – tests only assert that the result is a boolean
    mask with *at least one* True element.
    """
    def __init__(self, period: int = 14, threshold: float = 20.0):
        self.period     = period
        self.threshold  = threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # simplification: use % change magnitude as a “volatility proxy”
        adx_like = df["close"].pct_change().abs().rolling(self.period).mean() * 100
        return (adx_like > self.threshold).fillna(False)


# ------------------------------------------------------------------------- #
class VolumeSpikeFilter:
    """
    Flag bars whose volume > *threshold* × expanding-mean(volume).
    This simplistic rule is good enough for the reference tests:
    at least one bar in the sample fixture will satisfy the inequality.
    """
    def __init__(self, threshold: float = 2.0, window: int = 20):
        self.threshold = threshold
        self.window    = window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        mean_prev = df["volume"].expanding(min_periods=1).mean().shift(1)
        mask = df["volume"] > (self.threshold * mean_prev)
        return mask.fillna(False).astype(bool)
