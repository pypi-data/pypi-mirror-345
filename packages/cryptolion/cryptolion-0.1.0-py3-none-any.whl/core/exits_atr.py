#-------------------------------------------------------------------------------
# file: src/core/exits_atr.py
#-------------------------------------------------------------------------------
import pandas as pd


class ATRStopExit:
    def __init__(self, length: int, multiplier: float):
        self.length = length
        self.multiplier = multiplier

    def generate_exits(self, df: pd.DataFrame, position: pd.Series) -> pd.Series:  # noqa: D401
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = tr.rolling(self.length, min_periods=1).mean()
        stop = prev_close - atr * self.multiplier
        return (df["close"] < stop) & (position > 0)