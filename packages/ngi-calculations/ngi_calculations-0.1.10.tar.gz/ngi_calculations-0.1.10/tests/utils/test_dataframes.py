from math import nan

import pandas as pd
import pytest
from pytest import dict_parametrize

from ngi_calculations.cpt_correlations.utils.dataframes import find_n_closest_rows, merge_dataframe_on_column, safe_return


@dict_parametrize(
    {
        "Should return the safe_value if the dataframe is None": {
            "df": pd.DataFrame({}),
            "col": "A",
            "index": 0,
            "safe_value": 1.0,
            "expected": 1.0,
        },
        "Should return the safe_value if the dataframe is empty": {
            "df": pd.DataFrame({}),
            "col": "A",
            "index": 0,
            "safe_value": 1.0,
            "expected": 1.0,
        },
        "Should return the safe_value if the index not in the dataframe": {
            "df": pd.DataFrame({"A": [0.5]}),
            "col": "A",
            "index": 1,
            "safe_value": 1.0,
            "expected": 1.0,
        },
        "Should return the safe_value if the column not in the dataframe": {
            "df": pd.DataFrame({"A": [0.5]}),
            "col": "B",
            "index": 0,
            "safe_value": 1.0,
            "expected": 1.0,
        },
        "Should return the safe_value if the value is None": {
            "df": pd.DataFrame({"A": [None]}),
            "col": "A",
            "index": 0,
            "safe_value": 1.0,
            "expected": 1.0,
        },
        "Should return the safe_value if the value is NaN": {
            "df": pd.DataFrame({"A": [nan]}),
            "col": "A",
            "index": 0,
            "safe_value": 1.0,
            "expected": 1.0,
        },
        "Should return the value if the value is found": {
            "df": pd.DataFrame({"A": [0.5]}),
            "col": "A",
            "index": 0,
            "safe_value": 1.0,
            "expected": 0.5,
        },
    }
)
def test_safe_return(df, col, index, safe_value, expected) -> None:
    result = safe_return(df, index, col, safe_value)
    assert result == expected


INPUT_DF = pd.DataFrame({"a": [0, 1, 2, 3], "b": [0.1, 0.2, 0.3, 0.4]})


@dict_parametrize(
    {
        "Should return the correct selection - case 1": {
            "df": INPUT_DF,
            "lookup_column": "a",
            "lookup_value": 2.5,
            "n": 2,
            "expected": INPUT_DF.iloc[[2, 3]],
        },
        "Should return the correct selection - case 2": {
            "df": INPUT_DF,
            "lookup_column": "a",
            "lookup_value": 4.5,
            "n": 2,
            "expected": INPUT_DF.iloc[[2, 3]],
        },
        "Should return the correct selection - case 3": {
            "df": INPUT_DF,
            "lookup_column": "a",
            "lookup_value": -4.5,
            "n": 2,
            "expected": INPUT_DF.iloc[[0, 1]],
        },
    },
)
def test_find_n_closest_rows(df, lookup_column, lookup_value, n, expected):
    result = find_n_closest_rows(df, lookup_column, lookup_value, n)
    assert result.equals(expected)


df1 = pd.DataFrame({"a": [0, 1, 2, 3], "b": ["a", "b", "c", "d"]})
df2 = pd.DataFrame({"a": [0, 1, 2, 3], "c": [0.1, 0.2, 0.3, 0.4]})
df3 = pd.DataFrame({"a": [0, 1, 2, 4], "c": [0.1, 0.2, 0.3, 0.4]})
df4 = pd.DataFrame({"a": [4], "c": [0.4]})
df5 = pd.DataFrame({"b": [4], "d": [0.4]})

dfm1 = pd.DataFrame({"a": [0, 1, 2, 3], "b": ["a", "b", "c", "d"], "c": [0.1, 0.2, 0.3, 0.4]})
dfm2 = pd.DataFrame({"a": [0, 1, 2, 3, 4], "b": ["a", "b", "c", "d", nan], "c": [0.1, 0.2, 0.3, nan, 0.4]})
dfm3 = pd.DataFrame({"a": [0, 1, 2, 3, 4], "b": ["a", "b", "c", "d", nan], "c": [0.1, 0.2, 0.3, nan, 0.4]})


@dict_parametrize(
    {
        "Should return the correct merged dataframe (1)": {"input": [df1, df2], "on": "a", "expected": dfm1},
        "Should return the correct merged dataframe (2)": {"input": [df1, df3], "on": "a", "expected": dfm2},
        "Should return the correct merged dataframe (3)": {"input": [df1, df3], "on": "a", "expected": dfm3},
        "Should return the correct merged dataframe (4)": {"input": [df1, df1], "on": "a", "expected": df1},
        "Should return the correct merged dataframe (5)": {"input": [], "on": "a", "expected": None},
        "Should return the correct merged dataframe (6)": {"input": [df4, df5], "on": "a", "expected": None},
    }
)
def test_merge_dataframe_on_column(input, on, expected):
    if isinstance(expected, pd.DataFrame):
        assert merge_dataframe_on_column(input, on).equals(expected)
    else:
        # expect to raise value error
        if len(input) == 0:
            with pytest.raises(ValueError):
                merge_dataframe_on_column(input, on)
