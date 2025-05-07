import pandas as pd
import pytest
from core.strategy import StrategyEngine

@pytest.fixture
def simple_df():
    idx = pd.date_range('2025-01-01', periods=5, freq='min')
    prices = [100, 105, 110, 100, 95]
    df = pd.DataFrame({'close': prices}, index=idx)
    entries = pd.Series([0,1,0,0,0], index=idx)
    exits   = pd.Series([0,0,1,0,0], index=idx)
    sizes   = pd.Series([0,1,1,1,1], index=idx)
    return df, entries, exits, sizes

def test_simple_strategy(simple_df):
    df, entries, exits, sizes = simple_df
    engine = StrategyEngine(100)
    equity = engine.run(df, entries, exits, sizes)
    assert equity.iloc[2] == pytest.approx(105)  # 1*(110-105)+100
    assert equity.iloc[3] == pytest.approx(105)
