from __future__ import annotations

import pandas as pd


class VolumeSpikeFilter:
    """
    Emits **True** on bars where the current volume is
    *threshold ×* the rolling mean of the preceding `window`
    bars (baseline is *shifted* so that a spike is compared
    against *previous* activity only).

    Parameters
    ----------
    threshold : float
        e.g. 2.0  → “≥ 200 % of average volume”.
    window : int
        Look-back length for the moving average.
    """

    def __init__(self, threshold: float = 2.0, window: int = 20) -> None:
        self.threshold = float(threshold)
        self.window    = int(window)

    # -----------------------------------------------------------------
    # public API
    # -----------------------------------------------------------------
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        if "volume" not in df.columns:
            raise KeyError("'volume' column required")

        vol        = df["volume"].astype(float)
        baseline   = vol.rolling(self.window, min_periods=1).mean().shift(1)
        spike_mask = vol >= self.threshold * baseline

        # NaNs (first bar) → False; return boolean dtype
        return spike_mask.fillna(False)
