import pandas as pd
from tests.data.import_from_excel import rename_excel_df_columns


def test_rename_and_duplicate_columns():
    # Create a sample DataFrame
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

    # Define the renaming and duplicating dictionary
    columns_mapping = {"A": "D", "B": ["E", "F"], "C": "G"}

    df_renamed = rename_excel_df_columns(df, columns_mapping)
    df_renamed.sort_index(axis=1, inplace=True)  # Sort the columns to make the comparison easier

    expected_df = pd.DataFrame({"D": [1, 2, 3], "E": [4, 5, 6], "F": [4, 5, 6], "G": [7, 8, 9]})

    assert df_renamed.columns.equals(expected_df.columns)
    assert df_renamed.equals(expected_df)

