from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)
        self.trades: list[dict] = []

    @abstractmethod
    def generate_signals(self, bar_index: int) -> int:
        ...

    def run(self):
        for i in range(len(self.df)):
            self.generate_signals(i)
        return self.trades