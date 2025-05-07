import pandas as pd
from cryptolion.strategies.ultra import UltraStrategy

def test_ma_cross_entry():
    df = pd.read_csv("tests/data/ma_cross_fixture.csv", parse_dates=["date"]).set_index("date")
    strat = UltraStrategy(df)
    for i in range(len(df)):
        sig = strat.generate_signals(i)
    # assert first trade taken on expected bar
    assert strat.trades[0].entry_bar == 42
