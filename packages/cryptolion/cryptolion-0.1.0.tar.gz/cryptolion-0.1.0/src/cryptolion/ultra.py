# src/cryptolion/ultra.py
import pandas as pd
from core.entries import MaCrossEntry

class Trade:
    def __init__(self, entry_bar, exit_bar):
        self.entry_bar = entry_bar
        self.exit_bar = exit_bar

class UltraStrategy:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.entry_rule = MaCrossEntry(short=5, long=20)  # or from fixture
        self.trades = []

    def generate_signals(self, bar: int) -> bool:
        # return True/False for entry at bar
        s = self.entry_rule.generate_signals(self.df).iloc[bar]
        if s:
            self.trades.append(Trade(entry_bar=bar, exit_bar=None))
        return s
