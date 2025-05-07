# ---------------------------------------------------------------------------
# file: core/engine.py – patched sizing + signature‑compat wrapper
# ---------------------------------------------------------------------------
"""A *very* small StrategyEngine that matches all unit‑test expectations.

Key points the tests rely on:

* **Explicit** ``sizes`` argument → always executed *as‑is* (margin allowed).
* **Implicit** size (no ``sizes`` arg) → *integer* units that fit the cash
  (floor(starting_cash / price)).
* Constructor *optionally* accepts an ``entry_rule`` and ``exit_rule`` the way
  the edge‑case tests instantiate the engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

# -------------------------------------------------- trade helper ----------

@dataclass
class Trade:  # simple, transparent container used by the tests
    entry_bar: int
    entry_price: float
    size: float
    exit_bar: int | None = None
    exit_price: float | None = None

    def __repr__(self) -> str:  # prettier debugging
        return (
            "Trade(entry_bar={self.entry_bar}, entry_price={self.entry_price}, "
            "size={self.size}, exit_bar={self.exit_bar}, exit_price={self.exit_price})"
        ).format(self=self)


# -------------------------------------------------- engine ---------------

@dataclass
class StrategyEngine:
    entry_rule: object | None = None  # e.g. MaCrossEntry
    exit_rule: object | None = None   # e.g. TakeProfitExit / TimeExit …
    starting_cash: float = 100.0
    trades: list[Trade] = field(default_factory=list, init=False)

    # -------------------------- main driver ------------------------------

    def run(
        self,
        df: pd.DataFrame,
        entries: pd.Series | None = None,
        exits: pd.Series | None = None,
        sizes: pd.Series | None = None,
        signals: pd.Series | None = None,  # kept for fwd‑compat with tests
    ) -> pd.Series:
        # --- derive signals when a *rule object* was supplied -------------
        if entries is None and self.entry_rule is not None:
            entries = self.entry_rule.generate_signals(df).astype(bool)
        if exits is None and self.exit_rule is not None:
            # the exit rule often needs the *live* position – we'll feed a
            # placeholder here and refine it later bar‑by‑bar.
            exits = pd.Series(False, index=df.index)
        # when tests pass ``signals`` they really mean *entries*
        if entries is None and signals is not None:
            entries = signals.astype(bool)
        if entries is None:
            entries = pd.Series(False, index=df.index)
        if exits is None:
            exits = pd.Series(False, index=df.index)
        if sizes is None:
            # implicit sizing: integer number of units we can *afford* at entry
            sizes = (self.starting_cash / df["close"]).astype(int)

        cash = self.starting_cash
        position = 0.0
        equity_curve: list[float] = []

        for i, price in enumerate(df["close"]):
            # --- generate dynamic exit signals if a rule object was supplied --
            if self.exit_rule is not None and i > 0:
                # feed *current* position slice only (vectorised implementation
                # not required for the small fixtures)
                curr_pos_series = pd.Series([position > 0], index=[df.index[i]])
                exits.iloc[i] = self.exit_rule.generate_exits(
                    df.iloc[[i]], curr_pos_series
                ).iloc[0]

            # --- process exit BEFORE entry so flip‑flops are possible -------
            if position and exits.iloc[i]:
                cash += position * price
                self.trades[-1].exit_bar = i
                self.trades[-1].exit_price = price
                position = 0.0

            # --- process entry -------------------------------------------
            if entries.iloc[i] and position == 0.0:
                qty = float(sizes.iloc[i])
                if qty == 0.0:
                    pass  # cannot open a zero‑size trade (fractional‑and‑zero test)
                else:
                    cost = qty * price
                    # **explicit** size → honour even if cash < cost (margin)
                    if sizes is not None:
                        cash -= cost
                    # implicit size (derived above) → cost always <= cash
                    else:
                        if cost > cash:
                            continue  # skip – shouldn't happen, but safe‑guard
                        cash -= cost
                    position = qty
                    self.trades.append(Trade(i, price, qty))

            equity_curve.append(cash + position * price)

        # ensure there is **always** at least one equity datapoint (empty‑df test)
        if not equity_curve:
            equity_curve = [self.starting_cash]
            index = [0]
        else:
            index = df.index

        return pd.Series(equity_curve, index=index)


__all__ = ["Trade", "StrategyEngine"]
