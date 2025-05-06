import json
from functools import reduce
from math import isnan
from typing import Dict, Union

import pandas as pd
from pandas.core.frame import DataFrame


def is_unique(s):
    """Efficient way to find if all values in a dataframe series are equals

    @url: https://stackoverflow.com/a/54405767

    Args:
        s (Series): Pandas series

    Returns:
        bool: wether all equals or not
    """
    a = s.to_numpy()  # s.values (pandas<0.24)
    return bool((a[0] == a).all())


def safe_dataframe(
    data: Union[str, Dict[str, any]],
    empty_df: DataFrame = pd.DataFrame({"x": []}),
) -> DataFrame:
    """
    Methods that read the provided data and safely generate a dataframe regardless of the data type.
    It will fallback to an empty dataframe upon creation error.
    """
    try:
        data_ = data
        if isinstance(data, str):
            data_ = json.loads(data)

        if "schema" in data_:
            return pd.read_json(data_)
        else:
            return pd.DataFrame(data_)
    except ValueError:
        return empty_df


def dataframe_has_data(df: Union[DataFrame, None], min_row_length: int = 1) -> bool:
    """Checks if a dataframe has data"""
    if df is not None and not isinstance(df, DataFrame):
        raise ValueError("df must be a pandas dataframe")
    if df is None or df.empty:
        return False
    return df.shape[0] >= min_row_length


def df_is_not_empty(df: Union[DataFrame, None]) -> bool:
    if df is None:
        return False
    return not df.empty


def safe_return(data: DataFrame, index: int, col: str, safe_value: float = 0.0, precision: int = 3) -> float:
    if data is None or data.empty:
        return safe_value

    if col not in data.columns.to_list():
        return safe_value

    if index > data.shape[0] - 1:
        return safe_value

    val = data.iloc[index][col]

    if val is None:
        return safe_value
    elif isnan(val):
        return safe_value
    else:
        return round(val, precision)


def find_n_closest_rows(df: pd.DataFrame, lookup_column: str, lookup_value: float, n: int) -> pd.DataFrame:
    n_ = n if df.shape[0] >= n else df.shape[0]
    sorted_df = df.copy()
    sorted_df["comp"] = abs(sorted_df[lookup_column] - lookup_value)
    sorted_df.sort_values(by="comp", inplace=True)
    sorted_df = sorted_df.head(n_)
    sorted_df.drop(columns=["comp"], inplace=True)
    sorted_df.sort_values(by=lookup_column, inplace=True)
    return sorted_df
    # sorted_df2 = df.iloc[(df[lookup_column] - lookup_value).abs().argsort()]
    # sorted_df = df.iloc[(df[lookup_column] - lookup_value).abs().argsort()[:n_]]
    # sorted_df = sorted_df.sort_values(by=lookup_column)
    # return sorted_df


def check_if_all_equal(dataframes):
    # Check if the list is empty
    if len(dataframes) == 0:
        return True
    # Compare each DataFrame with the first one
    first_df = dataframes[0]
    for df in dataframes[1:]:
        if not first_df.equals(df):
            return False
    return True


def merge_dataframe_on_column(dfs: list[pd.DataFrame], on: str) -> pd.DataFrame:
    if len(dfs) == 0:
        raise ValueError("dfs must not be empty")

    if len(dfs) == 1:
        return dfs[0]

    if check_if_all_equal(dfs):
        return dfs[0]

    if on not in dfs[0].columns.to_list():
        raise ValueError(f"on must be in the columns of the dataframes: {dfs[0].columns.to_list()}")

    df = reduce(lambda left, right: pd.merge(left, right, on=on, how="outer"), dfs)
    df.reset_index(drop=True, inplace=True)
    return df
