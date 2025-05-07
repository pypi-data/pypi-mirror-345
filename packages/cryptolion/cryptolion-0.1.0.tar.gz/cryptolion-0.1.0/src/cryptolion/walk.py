import pandas as pd
from .backtest  import run_backtest
from .strategy  import StrategyEngine

def run_walk(csv_in: str, windows: list[int], cash: float = 100_000, csv_out: str = None):
    df = pd.read_csv(csv_in, parse_dates=True, index_col=0)
    curves = {}
    for w in windows:
        eq = run_backtest(csv_in, csv_out=None, cash=cash, window=w)
        curves[f"win_{w}"] = eq
    out = pd.DataFrame(curves)
    if csv_out:
        out.to_csv(csv_out)
    return out
