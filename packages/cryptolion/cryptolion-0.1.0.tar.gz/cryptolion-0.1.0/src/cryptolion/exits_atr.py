import pandas as pd


def _compute_tr(df: pd.DataFrame) -> pd.Series:
    hl = df['high'] - df['low']
    hp = (df['high'] - df['close'].shift()).abs()
    lp = (df['low']  - df['close'].shift()).abs()
    return pd.concat([hl, hp, lp], axis=1).max(axis=1)

class ATRStopExit:
    def __init__(self, length: int, multiplier: float):
        self.length     = length
        self.multiplier = multiplier

    def generate_exits(self, df: pd.DataFrame, pos: pd.Series) -> pd.Series:
        tr  = _compute_tr(df)
        atr = tr.rolling(self.length).mean()
        hh  = df['high'].rolling(self.length).max()
        stop = hh - self.multiplier * atr
        mask = (df['close'] < stop) & pos.astype(bool)
        return mask.fillna(False)