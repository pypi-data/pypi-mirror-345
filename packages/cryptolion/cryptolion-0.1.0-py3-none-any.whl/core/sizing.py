# File: src/core/sizing.py
import pandas as pd

class ATRUnitSizer:
    def __init__(self, length: int, unit_size: float):
        self.length = length
        self.unit_size = unit_size

    def size_positions(self, df: pd.DataFrame, signals: pd.Series) -> pd.Series:
        return pd.Series(self.unit_size, index=df.index)

class FixedPctSizer:
    def __init__(self, pct: float):
        self.pct = pct

    def size_positions(self, df: pd.DataFrame, signals: pd.Series) -> pd.Series:
        return pd.Series(self.pct, index=df.index)

class KellySizer:
    def __init__(self, lookback: int, rf: float):
        self.lookback = lookback
        self.rf = rf

    def size_positions(self, df: pd.DataFrame, signals: pd.Series) -> pd.Series:
        rets = df["close"].pct_change().fillna(0)
        wins = rets.where(signals & (rets > 0)).dropna()
        losses = -rets.where(signals & (rets < 0)).dropna()
        if len(wins) + len(losses) == 0:
            return pd.Series(0, index=df.index)
        W = len(wins) / (len(wins) + len(losses))
        R = wins.mean() / max(1e-8, losses.mean())
        kelly = (W - (1 - W) / R).clip(0, 1)
        return pd.Series(kelly, index=df.index)