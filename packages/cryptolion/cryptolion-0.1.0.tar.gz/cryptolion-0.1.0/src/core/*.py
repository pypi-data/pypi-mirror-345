def run_backtest(
    csv_in: str,
    csv_out: Optional[str] = None,
    ...
) -> pd.Series:
    """
    Run a single backtest.

    Parameters
    ----------
    csv_in : str
        Path to OHLC CSV with DateTime index.
    csv_out : Optional[str]
        If given, path to write equity curve CSV.
    ema_fast : int
        Fast EMA window.
    ...
    
    Returns
    -------
    pd.Series
        Equity curve over time.
    """
    ...
