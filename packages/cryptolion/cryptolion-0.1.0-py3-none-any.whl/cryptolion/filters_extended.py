from cryptolion.filters.base import BaseFilter
import pandas as pd


class VolumeSpikeFilter(BaseFilter):
    """
    Filters bars where volume spikes relative to the expanding mean of prior bars.

    Parameters
    ----------
    threshold : float
        Multiplier above the expanding mean to mark a spike (e.g. 2.0 for 2× average).
    window : int
        Minimum number of prior bars required before detecting spikes.

    Returns
    -------
    pd.Series of bool
        True where volume ≥ threshold × expanding mean(volume) of prior bars,
        with at least `window` prior bars.
    """
    def __init__(self, threshold: float = 2.0, window: int = 20):
        self.threshold = threshold
        self.window = window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # extract volume series
        vol = df['volume']
        # shift to get only prior volumes
        prior_vol = vol.shift(1)
        # compute expanding mean on prior volumes, require minimum periods
        mean_expanding = prior_vol.expanding(min_periods=self.window).mean()
        # count of prior non-null volumes
        count_prior = prior_vol.expanding().count()
        # mark spikes where current volume >= threshold * mean and enough prior bars
        spikes = (vol >= self.threshold * mean_expanding) & (count_prior >= self.window)
        # ensure bool dtype, fill missing as False
        return spikes.fillna(False).astype(bool)
