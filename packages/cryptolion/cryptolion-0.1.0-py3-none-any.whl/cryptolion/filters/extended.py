import pandas as pd
from .base import Filter

class VolumeSpikeFilter(Filter):
    def __init__(self, threshold: float = 2.0, window: int = 20):
        """
        threshold: how many standard deviations above the rolling mean
        window:   look‐back period for mean/std
        """
        self.threshold = threshold
        self.window = window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        if 'volume' not in df:
            raise ValueError("DataFrame must contain a 'volume' column")

        # compute rolling mean & std of the *previous* window bars
        mean = df['volume'].rolling(window=self.window).mean().shift(1)
        std  = df['volume'].rolling(window=self.window).std(ddof=0).shift(1)

        spikes = df['volume'] > (mean + self.threshold * std)
        return spikes.fillna(False).astype(bool)
