import pandas as pd
from typing import Optional
from .strategy import StrategyEngine
from .entries  import EMACrossEntry
from .exits    import ProfitTargetExit, TimeExit
from .sizing   import FixedPctSizer

def run_backtest(csv_in: str,
                 csv_out: Optional[str] = None,
                 cash: float = 100_000):
    """CLI: load CSV, apply default rules, write equity."""
    df = pd.read_csv(csv_in, parse_dates=True, index_col=0)

    entry_rule = EMACrossEntry(12,26)
    exit_rule  = ProfitTargetExit(0.05)
    sizer      = FixedPctSizer(1.0)

    ent = entry_rule.generate_entries(df)
    ext = exit_rule.generate_exits(df, ent)
    sz  = sizer.size_positions(df, ent)

    engine = StrategyEngine(cash)
    eq = engine.run(df, ent, ext, sz)

    if csv_out:
        eq.to_csv(csv_out)
    else:
        print(eq.to_csv())
