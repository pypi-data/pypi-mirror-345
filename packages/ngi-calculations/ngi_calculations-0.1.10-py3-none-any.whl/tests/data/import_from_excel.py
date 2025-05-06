import pandas as pd
from openpyxl.utils import column_index_from_string

from tests.data.excel_import_model import ExcelDataConfig


def convert_to_letter(column_index):
    """
    Convert a numeric column index to its corresponding letter representation.
    For example: 1 -> 'A', 2 -> 'B', ..., 26 -> 'Z', 27 -> 'AA', 28 -> 'AB', ...
    """
    dividend = column_index
    column_letter = ""
    while dividend > 0:
        modulo = (dividend - 1) % 26
        column_letter = chr(65 + modulo) + column_letter
        dividend = (dividend - modulo) // 26

    return column_letter


def rename_excel_df_columns(df: pd.DataFrame, columns_mapping: dict[str, str | list[str]]) -> pd.DataFrame:
    """
    Renames the columns of a pandas DataFrame based on a specified mapping.
            to their new names.
    """
    df_copy = df.copy()
    for i, c in enumerate(df.columns):
        if c in columns_mapping:
            new_names = columns_mapping[c]
            if isinstance(new_names, list):
                for new_name in new_names:
                    df_copy[new_name] = df[c]
                df_copy.drop(columns=c, inplace=True)
            else:
                df_copy.rename(columns={c: new_names}, inplace=True)
        else:
            df_copy.rename(columns={c: f"_skip{i}"}, inplace=True)
    return df_copy


# Function to identify columns with numeric strings and convert them to float
def convert_numeric_string_columns(df):
    # Create a copy to avoid modifying the original dataframe
    df_copy = df.copy()

    # Loop through all columns in the dataframe
    for col in df_copy.columns:
        # Check if the column has string dtype
        if pd.api.types.is_string_dtype(df_copy[col]):
            # Try to convert the column to numeric
            try:
                # Convert string to numeric (will handle both int and float strings)
                numeric_col = pd.to_numeric(df_copy[col], errors="coerce")

                # If conversion worked without introducing new NaNs
                if not numeric_col.isna().all() and numeric_col.isna().sum() == df_copy[col].isna().sum():
                    # Explicitly cast to float64 type
                    df_copy[col] = numeric_col.astype("float64")
                    # print(f"Converted column '{col}' to float")
            except:
                continue

    # Now check for any integer columns and convert them to float as well
    for col in df_copy.columns:
        if pd.api.types.is_integer_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].astype("float64")
            # print(f"Converted integer column '{col}' to float")

    return df_copy


def import_excel_to_dataframe(
    file_path,
    config: ExcelDataConfig,
    # file_path, sheetname, start_column, end_column, start_row, end_row, columns_mapping: dict[str, str] = None
):
    """
    Imports data from an Excel file into a pandas DataFrame based on specified sheetname,
    column range, and row range.

    Parameters:
        file_path (str): The path to the Excel file.
        sheetname (str): The name of the sheet from which data will be read.
        start_column (str): The starting column letter (e.g., 'A', 'B', 'C') of the data range.
        end_column (str): The ending column letter (e.g., 'A', 'B', 'C') of the data range.
        start_row (int): The starting row number (1-indexed) of the data range.
        end_row (int): The ending row number (1-indexed) of the data range.
        columns_mapping (dict[str,str]): A dictionary that maps the original column names

    Returns:
        pandas.DataFrame: The extracted data as a pandas DataFrame.
    """
    try:
        # Convert column letters to numeric indices (0-indexed)
        start_column_index = column_index_from_string(config.start_column)
        end_column_index = column_index_from_string(config.end_column)
        columns = [convert_to_letter(i) for i in range(start_column_index, end_column_index + 1)]

        row_data_start = config.data_start_row - 1
        skip_rows = list(range(1, row_data_start - 1))

        # Read data from the specified Excel file and sheet
        df = pd.read_excel(
            file_path,
            sheet_name=config.sheetname,
            header=[config.header_row - 1],
            usecols=f"{config.start_column}:{config.end_column}",
            skiprows=skip_rows,
            nrows=config.data_end_row - config.data_start_row + 1,
        )

        df.columns = columns

        if config.column_mapping:
            df = rename_excel_df_columns(df, config.column_mapping)

        df = convert_numeric_string_columns(df)
        return df
    except Exception as e:
        print(f"Error occurred while importing data: {e}")
        return None
