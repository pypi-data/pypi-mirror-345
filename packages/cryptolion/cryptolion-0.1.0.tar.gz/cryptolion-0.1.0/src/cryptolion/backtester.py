#!/usr/bin/env python3
"""
cryptolion.backtester – simple CLI entry-point
Usage
-----
# single run
python -m cryptolion.backtester run \
    --file data/BTC_USDT_4h.csv \
    --strategy ultra \
    --params '{"entry_rule":"MA_CROSS","exit_rule":"TAKE_PROFIT"}'

# param grid (powerset)
python -m cryptolion.backtester grid \
    --file data/BTC_USDT_4h.csv \
    --strategy ultra \
    --grid  '{"entry_rule":["MA_CROSS","MACD"],"exit_rule":["TAKE_PROFIT","BREAKEVEN"]}'
"""

import argparse
import json
import itertools
import sys
import pandas as pd
from pathlib import Path
from importlib import import_module

# ---------- strategy registry ----------
STRATS = {
    "ultra": "cryptolion.strategies.ultra:UltraStrategy",
    # add other strategies here
}

def load_strategy(name):
    if name not in STRATS:
        sys.exit(f"Unknown strategy '{name}'. Available: {list(STRATS.keys())}")
    module_path, cls_name = STRATS[name].split(":")
    mod = import_module(module_path)
    return getattr(mod, cls_name)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # run command
    run_p = subparsers.add_parser("run", help="single backtest run")
    run_p.add_argument("--file", required=True, help="CSV file with Date,Open,High,Low,Close,Volume")
    run_p.add_argument("--strategy", default="ultra", help="Strategy name to use")
    run_p.add_argument("--params", default="{}", help="JSON dict of strategy parameters")

    # grid command
    grid_p = subparsers.add_parser("grid", help="grid search over parameters")
    grid_p.add_argument("--file", required=True, help="CSV file with Date,Open,High,Low,Close,Volume")
    grid_p.add_argument("--strategy", default="ultra", help="Strategy name to use")
    grid_p.add_argument("--grid", default="{}", help="JSON dict of lists for param grid")

    args = parser.parse_args()

    csv_path = Path(args.file)
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path, parse_dates=["date"]).set_index("date")

    StratCls = load_strategy(args.strategy)

    if args.cmd == "run":
        params = json.loads(args.params)
        strat = StratCls(df, **params)
        stats, trades = strat.backtest()
        print(stats.to_markdown())

    else:  # grid search
        grid = json.loads(args.grid)
        if not isinstance(grid, dict):
            sys.exit("Grid must be a JSON object mapping param names to lists")
        keys = list(grid.keys())
        values = list(grid.values())
        best = None
        for combo in itertools.product(*values):
            params = dict(zip(keys, combo))
            strat = StratCls(df, **params)
            stats, _ = strat.backtest()
            sharpe = stats.get("sharpe")
            print(f"Params {params} -> Sharpe {sharpe}")
            if sharpe is not None and (best is None or sharpe > best[0]):
                best = (sharpe, params, stats)
        if best:
            print("\n== Best Result ==")
            print(best[1])
            print(best[2].to_markdown())


if __name__ == "__main__":
    main()
