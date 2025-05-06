"""Calculate rolling features."""

# pylint: disable=too-many-branches
import datetime

import pandas as pd

from .columns import DELIMITER

_DAYS_COLUMN_SUFFIX = "days"
_ALL_SUFFIX = "all"
_COUNT_WINDOW_FUNCTION = "count"
_SUM_WINDOW_FUNCTION = "sum"
_MEAN_WINDOW_FUNCTION = "mean"
_MEDIAN_WINDOW_FUNCTION = "median"
_VAR_WINDOW_FUNCTION = "var"
_STD_WINDOW_FUNCTION = "std"
_MIN_WINDOW_FUNCTION = "min"
_MAX_WINDOW_FUNCTION = "max"
_SKEW_WINDOW_FUNCTION = "skew"
_KURT_WINDOW_FUNCTION = "kurt"
_SEM_WINDOW_FUNCTION = "sem"
_RANK_WINDOW_FUNCTION = "rank"
_WINDOW_FUNCTIONS = [
    _COUNT_WINDOW_FUNCTION,
    _SUM_WINDOW_FUNCTION,
    _MEAN_WINDOW_FUNCTION,
    _MEDIAN_WINDOW_FUNCTION,
    _VAR_WINDOW_FUNCTION,
    _STD_WINDOW_FUNCTION,
    _MIN_WINDOW_FUNCTION,
    _MAX_WINDOW_FUNCTION,
    _SKEW_WINDOW_FUNCTION,
    _KURT_WINDOW_FUNCTION,
    _SEM_WINDOW_FUNCTION,
    _RANK_WINDOW_FUNCTION,
]


def rolling_process(
    df: pd.DataFrame,
    windows: list[datetime.timedelta | None],
    on: str | None,
    features: list[str],
) -> pd.DataFrame:
    """Process margins between teams."""
    if not windows:
        return df
    for feature in features:
        for window in windows:
            window_df = (
                df.rolling(window, on=on) if window is not None else df.expanding()
            )
            window_col = (
                str(window.days) + _DAYS_COLUMN_SUFFIX
                if window is not None
                else _ALL_SUFFIX
            )
            for window_func in _WINDOW_FUNCTIONS:
                column = DELIMITER.join([feature, window_func, window_col])
                if window_func == _COUNT_WINDOW_FUNCTION:
                    df[column] = window_df[feature].count()
                elif window_func == _SUM_WINDOW_FUNCTION:
                    df[column] = window_df[feature].sum()
                elif window_func == _MEAN_WINDOW_FUNCTION:
                    df[column] = window_df[feature].mean()
                elif window_func == _MEDIAN_WINDOW_FUNCTION:
                    df[column] = window_df[feature].median()
                elif window_func == _VAR_WINDOW_FUNCTION:
                    df[column] = window_df[feature].var()
                elif window_func == _STD_WINDOW_FUNCTION:
                    df[column] = window_df[feature].std()
                elif window_func == _MIN_WINDOW_FUNCTION:
                    df[column] = window_df[feature].min()
                elif window_func == _MAX_WINDOW_FUNCTION:
                    df[column] = window_df[feature].max()
                elif window_func == _SKEW_WINDOW_FUNCTION:
                    df[column] = window_df[feature].skew()
                elif window_func == _KURT_WINDOW_FUNCTION:
                    df[column] = window_df[feature].kurt()
                elif window_func == _SEM_WINDOW_FUNCTION:
                    df[column] = window_df[feature].sem()
                elif window_func == _RANK_WINDOW_FUNCTION:
                    df[column] = window_df[feature].rank()
                else:
                    raise ValueError(f"Unrecognised window function: {window_func}")
    return df
