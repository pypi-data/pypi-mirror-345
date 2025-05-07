"""CLI entry‑point:  cryptolion [backtest|walk|report]"""
from argparse import ArgumentParser
from .backtest import run_backtest
from .walk import run_walk
from .report import run_report


def build_parser() -> ArgumentParser:
    p = ArgumentParser(prog="cryptolion", description="Cryptolion back‑tester CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    # back‑test ------------------------------------------------------------
    b = sp.add_parser("backtest", help="Run a single back‑test")
    b.add_argument("csv_in", help="Input OHLC CSV (index = datetime, cols=open,high,low,close)")
    b.add_argument("--cash", type=float, default=100_000, help="starting cash (default 100 k)")
    b.add_argument("--out", dest="csv_out", help="CSV file to save equity curve")
    b.set_defaults(run=lambda a: run_backtest(a.csv_in, a.csv_out, a.cash))

    # walk‑forward ---------------------------------------------------------
    w = sp.add_parser("walk", help="Walk‑forward analysis over one or more window sizes")
    w.add_argument("csv_in")
    w.add_argument("--window", type=int, nargs="+", required=True, help="window lengths")
    w.add_argument("--cash", type=float, default=100_000)
    w.add_argument("--out", dest="csv_out")
    w.set_defaults(run=lambda a: run_walk(a.csv_in, a.window, a.cash, a.csv_out))

    # report ---------------------------------------------------------------
    r = sp.add_parser("report", help="Generate stats / plot from equity CSV")
    r.add_argument("equity_csv")
    r.add_argument("--no-show", dest="show", action="store_false", help="suppress matplotlib window")
    r.set_defaults(run=lambda a: run_report(a.equity_csv, show=a.show))

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.run(args)

if __name__ == "__main__":
    main()