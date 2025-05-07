import pandas as pd
import matplotlib.pyplot as plt

def run_report(equity_csv: str, show: bool = True):
    eq = pd.read_csv(equity_csv, index_col=0).squeeze()
    r  = eq.pct_change().dropna()
    cum = eq.iloc[-1] / eq.iloc[0] - 1
    ann = (1 + cum) ** (252 / len(eq)) - 1
    vol = r.std() * 252**0.5
    print(f"Cumulative: {cum:.2%}\nAnnualised: {ann:.2%}\nVolatility: {vol:.2%}")
    if show:
        eq.plot(title="Equity curve")
        plt.show()