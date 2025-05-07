from __future__ import annotations
from typing import List
import pandas as pd

class Trade:
    def __init__(self, entry_bar: int, entry_price: float, size: float):
        self.entry_bar = entry_bar
        self.entry_price = entry_price
        self.size = size
        self.exit_bar: int | None = None
        self.exit_price: float | None = None

    @property
    def is_open(self) -> bool:
        return self.exit_bar is None

class StrategyEngine:
    _MAX_LEVERAGE = 10

    def __init__(
        self,
        entry_rule=None,
        exit_rule=None,
        starting_cash: float = 100.0,
    ):
        if isinstance(entry_rule, (int, float)) and exit_rule is None:
            starting_cash, entry_rule = float(entry_rule), None
        self.entry_rule = entry_rule
        self.exit_rule = exit_rule
        self.starting_cash = starting_cash
        self.trades: List[Trade] = []

    def run(
        self,
        df: pd.DataFrame,
        *pos,
        entries=None,
        exits=None,
        sizes=None,
        signals=None,
    ) -> pd.Series:
        # support positional args
        if pos:
            if len(pos) > 3:
                raise TypeError("Too many positional args")
            entries = pos[0] if len(pos) >=1 else entries
            exits   = pos[1] if len(pos) >=2 else exits
            sizes   = pos[2] if len(pos) >=3 else sizes

        # signals shorthand
        if signals is not None:
            b = signals.astype(bool)
            entries = b
            exits = (~b) & b.shift(1).fillna(False)

        if df.empty:
            return pd.Series([self.starting_cash], index=[0])

        entries = (
            entries.reindex(df.index, fill_value=False).astype(bool)
            if entries is not None else pd.Series(False, index=df.index)
        )
        exits = (
            exits.reindex(df.index, fill_value=False).astype(bool)
            if exits is not None else pd.Series(False, index=df.index)
        )
        sizes = (
            sizes.reindex(df.index, fill_value=1.0).astype(float)
            if sizes is not None else pd.Series(1.0, index=df.index)
        )

        cash = self.starting_cash
        units = 0.0
        equity: list[float] = []

        for i, (_, row) in enumerate(df.iterrows()):
            price = float(row["close"])

            # overlapping entry reposition
            if entries.iloc[i] and units > 0:
                prev = self.trades[-1]
                diff = price - prev.entry_price
                cash -= diff * units
                prev.entry_bar = i
                prev.entry_price = price

            # exit
            if units > 0 and exits.iloc[i]:
                cash += units * price
                prev = self.trades[-1]
                prev.exit_bar = i
                prev.exit_price = price
                units = 0.0

            # entry
            if units == 0 and entries.iloc[i] and sizes.iloc[i] > 0:
                cost = sizes.iloc[i] * price
                if cost <= self.starting_cash * self._MAX_LEVERAGE:
                    units = sizes.iloc[i]
                    cash -= units * price
                    self.trades.append(Trade(entry_bar=i, entry_price=price, size=units))

            equity.append(cash + units * price)

        return pd.Series(equity, index=df.index)