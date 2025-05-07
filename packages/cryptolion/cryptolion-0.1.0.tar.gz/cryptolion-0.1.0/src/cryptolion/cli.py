import argparse
from .backtest import run_backtest
from .walk     import run_walk
from .report   import run_report


def main():
    p = argparse.ArgumentParser(prog="cryptolion",
        description="CryptoLion backtester CLI")
    sub = p.add_subparsers(dest="cmd")

    b = sub.add_parser("backtest", help="Run a single backtest")
    b.add_argument("csv_in",  help="OHLC CSV in")
    b.add_argument("--out",   dest="csv_out", help="write equity CSV to")
    b.add_argument("--cash",  type=float, default=100_000,
                   help="starting cash")
    b.set_defaults(func=lambda a: run_backtest(a.csv_in, a.csv_out, a.cash))

    w = sub.add_parser("walk", help="Walk-forward analysis")
    w.add_argument("csv_in",  help="OHLC CSV in")
    w.add_argument("--window", nargs="+", type=int, required=True,
                   help="rolling window sizes, e.g. 50 100")
    w.add_argument("--cash",  type=float, default=100_000,
                   help="starting cash")
    w.add_argument("--out",   dest="csv_out", help="write walk equity CSV to")
    w.set_defaults(func=lambda a: run_walk(a.csv_in, a.window, a.cash, a.csv_out))

    r = sub.add_parser("report", help="Generate performance report")
    r.add_argument("equity_csv", help="equity CSV from backtest/walk")
    r.add_argument("--no-show", dest="show", action="store_false", default=True,
                   help="do not pop up the plot")
    r.set_defaults(func=lambda a: run_report(a.equity_csv, show=a.show))

    args = p.parse_args()
    if not hasattr(args, "func"):
        p.print_help()
        return 1
    return args.func(args)
