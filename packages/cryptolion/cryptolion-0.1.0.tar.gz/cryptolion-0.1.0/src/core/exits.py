#-------------------------------------------------------------------------------
# file: src/core/exits.py
# (unchanged – kept for context)
#-------------------------------------------------------------------------------
import pandas as pd
from .exits_atr import ATRStopExit


class ChandelierExit:
    def __init__(self, lookback: int, atr_length: int, multiplier: float):
        self.lookback = lookback
        self.atr_length = atr_length
        self.multiplier = multiplier

    def generate_exits(self, df: pd.DataFrame, position: pd.Series) -> pd.Series:
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = tr.rolling(self.atr_length, min_periods=1).mean()
        highest_high = df["high"].rolling(self.lookback, min_periods=1).max()
        stop = highest_high - atr * self.multiplier
        return (df["close"] < stop) & (position > 0)


class ProfitTargetExit:
    def __init__(self, target: float):
        self.target = target

    def generate_exits(self, df: pd.DataFrame, position: pd.Series) -> pd.Series:
        entry_mask = position.astype(int).diff().fillna(position).eq(1)
        entry_price = df["close"].where(entry_mask).ffill().fillna(0)
        threshold = entry_price * (1 + self.target)
        return (df["close"] >= threshold) & (position > 0)


class RSIExit:
    def __init__(self, length: int, threshold: float):
        self.length = length
        self.threshold = threshold

    def generate_exits(self, df: pd.DataFrame, position: pd.Series) -> pd.Series:
        delta = df["close"].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ma_up = up.rolling(self.length, min_periods=1).mean()
        ma_down = down.rolling(self.length, min_periods=1).mean()
        rs = ma_up / ma_down.replace(0, 1e-8)
        rsi = 100 - 100 / (1 + rs)
        return (rsi < self.threshold) & (position > 0)


class TimeExit:
    def __init__(self, max_bars: int):
        self.max_bars = max_bars

    def generate_exits(self, df: pd.DataFrame, position: pd.Series) -> pd.Series:
        entry_points = position.astype(int).diff().fillna(position).eq(1)
        trade_ids = entry_points.cumsum()
        bars_in_trade = trade_ids.where(position > 0, 0)
        bars_since_entry = bars_in_trade.groupby(trade_ids).cumcount()
        return (bars_since_entry >= self.max_bars) & (position > 0)