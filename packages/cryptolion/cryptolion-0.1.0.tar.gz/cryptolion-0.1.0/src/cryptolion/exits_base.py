from abc import ABC, abstractmethod
import pandas as pd

class ExitRule(ABC):
    @abstractmethod
    def generate_exits(self, df: pd.DataFrame, pos: pd.Series) -> pd.Series:
        """Return a boolean Series indicating where an open position should be closed."""
        ...
