"""The main process function."""

import datetime

import pandas as pd

from .lag_process import lag_process
from .non_categorical_numeric_columns import \
    find_non_categorical_numeric_columns
from .rolling_process import rolling_process
from .shift_process import shift_process


def process(
    df: pd.DataFrame,
    windows: list[datetime.timedelta | None] | None = None,
    lags: list[int] | None = None,
    on: str | None = None,
    shift: int = 1,
) -> pd.DataFrame:
    """Process the dataframe for timeseries features."""
    original_features = df.columns.values.tolist()
    features = find_non_categorical_numeric_columns(df)
    if lags is None:
        lags = []
    if windows is None:
        windows = []
    df = lag_process(df, lags, features)
    df = rolling_process(df, windows, on, features)
    added_features = [
        x for x in df.columns.values.tolist() if x not in original_features
    ]
    df = shift_process(df, features + added_features, shift)
    return df[sorted(df.columns.values.tolist())]
