#!/usr/bin/env python
import argparse
from core.backtest import run_backtest
from core.walk     import run_walk
from core.report   import run_report

def main():
    p = argparse.ArgumentParser(prog="backtester",
        description="CryptoLion backtester CLI")
    sp = p.add_subparsers(dest="cmd")
    sp.required = True

    # backtest
    b = sp.add_parser("backtest", help="Run a single backtest")
    b.add_argument("csv_in")
    b.add_argument("--out","-o",dest="csv_out")
    b.add_argument("--cash", type=float, default=100000)
    b.set_defaults(func=lambda a: run_backtest(a.csv_in, a.csv_out, a.cash))

    # walk
    w = sp.add_parser("walk", help="Walk‐forward analysis")
    w.add_argument("csv_in")
    w.add_argument("--window","-w", type=int, nargs="+", required=True)
    w.add_argument("--cash", type=float, default=100000)
    w.set_defaults(func=lambda a: run_walk(a.csv_in, a.window, a.cash))

    # report
    r = sp.add_parser("report", help="Generate report")
    r.add_argument("equity_csv")
    r.set_defaults(func=lambda a: run_report(a.equity_csv))

    args = p.parse_args()
    args.func(args)

if __name__=="__main__":
    main()
