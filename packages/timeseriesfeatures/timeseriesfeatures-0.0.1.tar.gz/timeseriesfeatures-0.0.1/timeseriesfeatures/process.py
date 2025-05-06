"""The main process function."""

import datetime

import pandas as pd

from .lag_process import lag_process
from .rolling_process import rolling_process


def process(
    df: pd.DataFrame,
    windows: list[datetime.timedelta | None] | None = None,
    lags: list[int] | None = None,
    on: str | None = None,
) -> pd.DataFrame:
    """Process the dataframe for timeseries features."""
    features = df.columns.values.tolist()
    if lags is None:
        lags = []
    if windows is None:
        windows = []
    df = lag_process(df, lags, features)
    df = rolling_process(df, windows, on, features)
    return df
