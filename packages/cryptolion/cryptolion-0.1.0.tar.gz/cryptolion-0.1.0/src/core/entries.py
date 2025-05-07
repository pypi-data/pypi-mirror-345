from __future__ import annotations
import pandas as pd

class BaseEntry:
    def generate_entries(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return self.generate_entries(df)

class MaCrossEntry(BaseEntry):
    def __init__(self, fast: int = 5, slow: int = 20):
        self.fast, self.slow = fast, slow

    def generate_entries(self, df: pd.DataFrame) -> pd.Series:
        fast = df["close"].rolling(self.fast).mean()
        slow = df["close"].rolling(self.slow).mean()
        return (fast > slow) & (fast.shift(1) <= slow.shift(1))

class EMACrossEntry(BaseEntry):
    def __init__(self, short: int = 12, long: int = 26):
        self.short, self.long = short, long

    def generate_entries(self, df: pd.DataFrame) -> pd.Series:
        if df.empty:
            return pd.Series(dtype=bool, index=df.index)
        fast = df["close"].ewm(span=self.short, adjust=False).mean()
        slow = df["close"].ewm(span=self.long, adjust=False).mean()
        sig  = (fast > slow) & (fast.shift(1) <= slow.shift(1))
        return sig.fillna(False)

class MACDEntry(BaseEntry):
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast, self.slow, self.signal = fast, slow, signal

    def generate_entries(self, df: pd.DataFrame) -> pd.Series:
        ema_fast = df["close"].ewm(span=self.fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=self.slow, adjust=False).mean()
        macd     = ema_fast - ema_slow
        macd_sig = macd.ewm(span=self.signal, adjust=False).mean()
        return (macd > macd_sig) & (macd.shift(1) <= macd_sig.shift(1))

class DonchianEntry(BaseEntry):
    def __init__(self, period: int = 20):
        self.period = period

    def generate_entries(self, df: pd.DataFrame) -> pd.Series:
        breakout = df["high"] > df["high"].rolling(self.period).max().shift(1)
        return breakout.fillna(False)

class RSIEntry(BaseEntry):
    def __init__(self, period: int = 14, threshold: float = 70.0):
        self.period, self.th = period, threshold

    def _rsi(self, series: pd.Series) -> pd.Series:
        delta = series.diff()
        gain  = delta.clip(lower=0).rolling(self.period).mean()
        loss  = -delta.clip(upper=0).rolling(self.period).mean()
        rs    = gain / loss.replace(0, pd.NA)
        return 100 - 100 / (1 + rs)

    def generate_entries(self, df: pd.DataFrame) -> pd.Series:
        rsi = self._rsi(df["close"])
        return (rsi > self.th) & (rsi.shift(1) <= self.th)