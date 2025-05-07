import pandas as pd

def run_report(equity_csv: str):
    """CLI: read equity CSV, print simple stats."""
    df = pd.read_csv(equity_csv, index_col=0)
    eq = df.iloc[:,0]
    total = eq.iloc[-1]/eq.iloc[0] - 1
    print(f"Total Return: {total:.2%}")
