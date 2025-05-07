import pandas as pd
from typing import Optional
from .strategy import StrategyEngine

def run_backtest(csv_in: str, csv_out: Optional[str] = None, cash: float = 100_000):
    df = pd.read_csv(csv_in, parse_dates=True, index_col=0)
    eq = StrategyEngine(cash).run(df)
    if csv_out:
        eq.to_csv(csv_out)
    return eq