import argparse, sys, textwrap
from pathlib import Path
from .backtest import run_backtest
from .walk import run_walk
from .report import summary

def cli() -> None:
    p = argparse.ArgumentParser(
        prog="cryptolion",
        description="CryptoLion backtester CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples
            --------
            cryptolion backtest ohlc.csv -c 50000 -o equity.csv
            cryptolion walk     ohlc.csv --window 50 100
            cryptolion report   equity.csv
            """
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    bt = sub.add_parser("backtest", help="Run a single backtest")
    bt.add_argument("csv_in")
    bt.add_argument("-c", "--cash", type=float, default=10_000)
    bt.add_argument("-o", "--out", dest="csv_out")

    wk = sub.add_parser("walk", help="Walk-forward")
    wk.add_argument("csv_in")
    wk.add_argument("--window", type=int, nargs="+", required=True)
    wk.add_argument("-c", "--cash", type=float, default=10_000)
    wk.add_argument("-o", "--out")

    rp = sub.add_parser("report", help="Generate performance report")
    rp.add_argument("equity_csv")

    args = p.parse_args()

    match args.cmd:
        case "backtest":
            eq = run_backtest(args.csv_in, args.csv_out, args.cash)
            print(summary(eq))
        case "walk":
            df = run_walk(args.csv_in, args.window, args.cash)
            if args.out:
                df.to_csv(args.out)
            print(df.iloc[-1].apply(lambda v: f"{v:.0f}"))
        case "report":
            import pandas as pd, matplotlib.pyplot as plt

            eq = pd.read_csv(args.equity_csv, index_col=0, squeeze=True)
            print(summary(eq))
            eq.plot(title="Equity curve")
            plt.show()

if __name__ == "__main__":
    cli()
