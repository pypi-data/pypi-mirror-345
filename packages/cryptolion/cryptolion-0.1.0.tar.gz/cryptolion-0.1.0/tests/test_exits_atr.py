import pandas as pd

from core.exits_atr import ATRStopExit


def make_df():
    """20-bar gently rising price series with matching index."""
    idx = pd.date_range("2025-01-01", periods=20, freq="min")
    base = pd.Series(range(20), index=idx) * 0.1 + 100  # align with idx
    return pd.DataFrame(
        {
            "open": base,
            "high": base + 0.2,
            "low": base - 0.2,
            "close": base,
        },
        index=idx,
    )


def test_atr_stop_exit_triggers():
    df = make_df()
    pos = pd.Series(1, index=df.index)  # long the whole time
    # force a big drop on the last bar to trip the stop
    df.loc[df.index[-1], "close"] = df["close"].iloc[-2] - 1.0

    exit_rule = ATRStopExit(length=3, multiplier=1.0)
    mask = exit_rule.generate_exits(df, pos)

    assert mask.iloc[-1], "ATRStopExit should trigger on the final bar"
