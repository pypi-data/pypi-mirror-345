# File: src/core/filters.py
import pandas as pd

class TrendFilter:
    def __init__(self, span: int):
        self.span = span

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ma = df["close"].rolling(self.span, min_periods=1).mean()
        return (df["close"] > ma).fillna(False)

class VolumeSpikeFilter:
    def __init__(self, threshold: float, window: int):
        self.threshold = threshold
        self.window = window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        avg_vol = df["volume"].shift(1).rolling(self.window, min_periods=1).mean()
        return (df["volume"] > avg_vol * self.threshold).fillna(False)

class ADXFilter:
    def __init__(self, length: int, threshold: float):
        self.length = length
        self.threshold = threshold

    def _atr(self, high, low, close):
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)
        return tr.rolling(self.length).mean().fillna(0)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        high, low, close = df["high"], df["low"], df["close"]
        plus_dm = ((high.diff() > low.diff()) & (high.diff() > 0)) * high.diff().clip(lower=0)
        minus_dm = ((low.diff() > high.diff()) & (low.diff() > 0)) * (-low.diff()).clip(lower=0)
        atr = self._atr(high, low, close).replace(0, 1e-9)
        plus_di = (plus_dm.ewm(alpha=1 / self.length, adjust=False).mean() / atr) * 100
        minus_di = (minus_dm.ewm(alpha=1 / self.length, adjust=False).mean() / atr) * 100
        dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-9) * 100
        adx = dx.rolling(self.length, min_periods=self.length).mean().fillna(0)
        return ((adx > self.threshold) & (close.diff().abs() > 0)).fillna(False)