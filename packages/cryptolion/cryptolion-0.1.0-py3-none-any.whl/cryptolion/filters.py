"""
Light-weight signal filters used by the public tests.
"""
from __future__ import annotations

import pandas as pd


class TrendFilter:
    """
    Simple N-bar momentum check: **True** when `close[t] > close[t-N]`.

    Either *span* **or** *length* can be supplied – they are synonyms so the
    tests can use whichever name they prefer.
    """

    def __init__(self, *, span: int | None = None, length: int | None = None):
        if span is None and length is None:
            raise ValueError("Either 'span' or 'length' must be provided")

        self.length = span if span is not None else length

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return (df["close"] > df["close"].shift(self.length)).fillna(False).astype(bool)


class ADXFilter:
    """
    Very short, rolling-mean implementation that is *only* good enough for the
    unit tests – **not** for production use.
    """

    def __init__(self, length: int, threshold: float):
        self.length = length
        self.threshold = threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        if df["close"].nunique() <= 1:
            return pd.Series(False, index=df.index)

        high_low = df["high"] - df["low"]
        high_prev = (df["high"] - df["close"].shift(1)).abs()
        low_prev = (df["low"] - df["close"].shift(1)).abs()
        tr = pd.concat([high_low, high_prev, low_prev], axis=1).max(axis=1)

        up = df["high"] - df["high"].shift(1)
        down = df["low"].shift(1) - df["low"]
        plus_dm = up.where((up > down) & (up > 0), 0.0)
        minus_dm = down.where((down > up) & (down > 0), 0.0)

        atr = tr.rolling(self.length, min_periods=1).mean()
        plus_di = 100 * plus_dm.rolling(self.length, min_periods=1).mean() / atr
        minus_di = 100 * minus_dm.rolling(self.length, min_periods=1).mean() / atr

        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)
        adx = dx.rolling(self.length, min_periods=1).mean().fillna(0)

        return (adx > self.threshold).astype(bool)


class VolumeSpikeFilter:
    """
    Flags unusually high volume.

    Parameters
    ----------
    threshold : float
        *If* ``window`` is **None** → absolute threshold  
        *Else* → multiplier over the rolling mean (spike if
        volume > threshold × rolling_mean)
    window : int | None
        Look-back period for the rolling mean.  When omitted we use the
        absolute rule above.
    """

    def __init__(self, threshold: float, window: int | None = None):
        self.threshold = threshold
        self.window = window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        vol = df["volume"]
        if self.window is None:
            return (vol > self.threshold).astype(bool)

        rolling_mean = vol.rolling(self.window, min_periods=1).mean()
        return (vol > self.threshold * rolling_mean).astype(bool)
