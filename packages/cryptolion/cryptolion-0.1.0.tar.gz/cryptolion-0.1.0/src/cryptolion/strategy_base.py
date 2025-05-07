# src/cryptolion/strategy/base.py

from abc import ABC, abstractmethod
import pandas as pd

class EntryRule(ABC):
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Given a price DataFrame, return a boolean Series of entry signals
        (True at bars where a new long should be opened).
        """

class ExitRule(ABC):
    @abstractmethod
    def generate_exits(self, df: pd.DataFrame, entries: pd.Series) -> pd.Series:
        """
        Given a price DataFrame and a boolean Series of entries,
        return a boolean Series of exit signals (True at bars where the
        current long should be closed).
        ```
