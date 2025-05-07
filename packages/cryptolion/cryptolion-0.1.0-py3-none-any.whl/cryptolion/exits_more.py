"""Miscellaneous exit rules used by the tests."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .exits import ExitRule
from .exits_atr import _atr


class RSIExit(ExitRule):
    """Exit when RSI drops *below* a threshold while in a long."""

    def __init__(self, length: int = 14, threshold: float = 70):
        self.p, self.th = length, threshold

    @staticmethod
    def _rsi(src: pd.Series, p: int) -> pd.Series:
        d = src.diff()
        up, dn = d.clip(lower=0), -d.clip(upper=0)
        roll_up  = up.ewm(alpha=1 / p, adjust=False).mean()
        roll_down = dn.ewm(alpha=1 / p, adjust=False).mean().replace(0, np.nan)
        rs = roll_up / roll_down
        return 100 - 100 / (1 + rs)

    def generate_exits(self, df: pd.DataFrame, pos: pd.Series) -> pd.Series:
        rsi   = self._rsi(df["close"], self.p)
        cross = (rsi < self.th) & (rsi.shift() >= self.th)
        return (pos > 0) & cross


class ChandelierExit(ExitRule):
    """Classic chandelier stop (hi-max minus k×ATR)."""

    def __init__(self, lookback: int = 22, atr_length: int = 22, multiplier: float = 3):
        self.lb, self.len, self.k = lookback, atr_length, multiplier

    def generate_exits(self, df: pd.DataFrame, pos: pd.Series) -> pd.Series:
        atr  = _atr(df, self.len)
        hi   = df["high"].rolling(self.lb, 1).max()
        stop = hi - self.k * atr
        return (pos > 0) & (df["close"] < stop)
