"""Calculate lag features."""

import pandas as pd

from .columns import DELIMITER


def lag_process(df: pd.DataFrame, lags: list[int], features: list[str]) -> pd.DataFrame:
    """Process margins between teams."""
    if not lags:
        return df
    for feature in features:
        for lag in lags:
            column = DELIMITER.join([feature, "lag", str(lag)])
            df[column] = df[feature].shift(lag)
    return df
