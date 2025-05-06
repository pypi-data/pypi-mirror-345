from dataclasses import dataclass


@dataclass
class ExcelDataConfig:
    sheetname: str
    header_row: int
    start_column: str
    end_column: str
    data_start_row: int
    data_end_row: int
    column_mapping: dict
