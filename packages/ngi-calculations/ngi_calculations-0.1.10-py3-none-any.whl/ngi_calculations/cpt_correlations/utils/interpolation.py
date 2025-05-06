from typing import Literal

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


def set_replace_columns(df: pd.DataFrame, col_list: list[str]) -> list[str]:
    # Get the columns where interpolation should be performed (any column with NaN)
    return col_list if col_list else df.columns[df.isna().any()].tolist()


def interpolate_missing_values__padding_method(df: pd.DataFrame, inplace: bool = False, col_list: list[str] = []):
    # Whether to mutate the provided DataFrame or not
    _df = df if inplace else df.copy()

    # Get the columns where interpolation should be performed
    _cols = set_replace_columns(_df, col_list)

    for col in _cols:
        _df[col] = _df[col].ffill()

    return _df


def interpolate_missing_values__linear_method(
    df: pd.DataFrame, key_col: str, inplace: bool = False, col_list: list[str] = []
):
    # Whether to mutate the provided DataFrame or not
    _df = df if inplace else df.copy()

    # Get the columns where interpolation should be performed
    _cols = set_replace_columns(_df, col_list)

    # Store the key col values as a numpy array
    key_values = np.array(_df[key_col].values.tolist())

    # iterate over the columns that contains NaN
    for col in _cols:
        _values = _df[[key_col, col]].dropna()  # DataFrame of existing values in col

        col_values_finite = np.array(_values[col].values.tolist())  # Array of existing values in col

        key_values_finite = np.array(_values[key_col].values.tolist())  # Array of existing values in col

        if col_values_finite.size > 0:
            # Set-up the interpolation function (it must be done again for each column)
            f = interp1d(key_values_finite, col_values_finite, fill_value="extrapolate")
            # Set the interpolate data
            _df[col] = f(key_values)

    return _df


def interpolate_missing_values(
    df: pd.DataFrame,
    key_col: str = "depth",
    inplace: bool = False,
    col_list: list[str] = [],
    mode: Literal["linear", "padding"] = "linear",
):
    return (
        interpolate_missing_values__linear_method(df, key_col, inplace, col_list)
        if mode == "linear"
        else interpolate_missing_values__padding_method(df, inplace, col_list)
    )
