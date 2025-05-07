import pandas as pd
from cryptolion.engine import StrategyEngine
from cryptolion.entries import MaCrossEntry
from cryptolion.exits  import TakeProfitExit

def make_price():
    idx = pd.date_range("2025-01-01", periods=6, freq="min")
    return pd.DataFrame({"close": [100, 105, 110, 108, 107, 106]}, index=idx)

def test_fractional_and_zero_size():
    df = make_price()
    eng = StrategyEngine(MaCrossEntry(1, 2), TakeProfitExit(1), starting_cash=1.0)  # tiny cash
    eq  = eng.run(df)
    # no trade should be opened (size zero)
    assert len(eng.trades) == 0
    assert eq.iloc[-1] == 1.0
