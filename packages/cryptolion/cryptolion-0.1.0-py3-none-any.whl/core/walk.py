from typing import List
from .backtest import run_backtest
import pandas as pd

def run_walk(csv_in: str,
             windows: List[int],
             cash: float = 100_000) -> pd.DataFrame:
    """CLI: run `run_backtest` over each window, return wide DF."""
    out = {}
    for w in windows:
        eq = run_backtest(csv_in, None, cash) \
               .rename(f"window_{w}")
        out[f"window_{w}"] = eq
    return pd.DataFrame(out)
