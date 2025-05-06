import os
from dataclasses import dataclass
from enum import Enum

import pandas as pd

from ngi_calculations.cpt_correlations.models.cpt_cone import CptCone
from tests.data.excel_data_column_mapping import (
    CptProcessedColumns,
    CptRawColumns,
    LabDataColumns,
)
from tests.data.import_from_excel import import_excel_to_dataframe

# TODO: finish implementing the excel mapping for all the files


@dataclass
class ExcelDataConfig:
    sheetname: str
    header_row: int
    start_column: str
    end_column: str
    data_start_row: int
    data_end_row: int
    column_mapping: dict


@dataclass
class ExcelInterpretationNktNduConfig:
    Nkt: float
    Ndu: float


@dataclass
class ExcelInterpretationKarlsrud2005Config:
    OCR_profile: pd.DataFrame


@dataclass
class ExcelInterpretationPaniagua2019Config:
    OCR_profile: pd.DataFrame
    factorK: float = 0.15


@dataclass
class ExcelInterpretationSHANSEPConfig:
    OCR_profile: pd.DataFrame
    elevation_agingFactor: float = 1.0
    elevation_offloadedUW: float = 18.5
    elevation_previousLevel: float = 0.0
    elevation_currentLevel: float = 0.0
    factorAlpha: float = 0.3
    factorM: float = 0.8
    Nc_factor: float = 0.3


@dataclass
class ExcelInterpretationGlobalOptionsConfig:
    maxSu: float
    max_p_cons: float
    maxOCR: float


@dataclass
class ExcelInterpretation:
    NktNdu: ExcelInterpretationNktNduConfig
    Karlsrud2005: ExcelInterpretationKarlsrud2005Config
    Paniagua2019: ExcelInterpretationPaniagua2019Config
    SHANSEP: ExcelInterpretationSHANSEPConfig
    global_options: ExcelInterpretationGlobalOptionsConfig


@dataclass
class ExcelLabData:
    u0: ExcelDataConfig
    uw: ExcelDataConfig
    the_rest: ExcelDataConfig


@dataclass
class ExcelFileConfig:
    filename: str
    lab_data: ExcelDataConfig
    raw_cpt: ExcelDataConfig
    processed_cpt: ExcelDataConfig
    cone: dict[str, CptCone]


@dataclass
class ExcelDataConfig:
    sheetname: str
    header_row: int
    start_column: str
    end_column: str
    data_start_row: int
    data_end_row: int
    column_mapping: dict


class Files2(Enum):
    testA = ExcelFileConfig(
        filename="testA.xlsx",
        raw_cpt=ExcelDataConfig(
            sheetname="cpt_raw",
            start_column="A",
            end_column="I",
            header_row=2,
            data_start_row=4,
            data_end_row=439,
            column_mapping=CptRawColumns().columns,
        ),
        lab_data=ExcelDataConfig(
            sheetname="lab_data",
            start_column="A",
            end_column="H",
            header_row=2,
            data_start_row=4,
            data_end_row=10,
            column_mapping=LabDataColumns().columns,
        ),
        processed_cpt=ExcelDataConfig(
            sheetname="cpt_processed",
            start_column="A",
            end_column="AF",
            header_row=2,
            data_start_row=4,
            data_end_row=439,
            column_mapping=CptProcessedColumns().columns,
        ),
        cone={
            "aaa": CptCone(cone_area_ratio=0.85, sleeve_area_ratio=1.0),
            "bbb": CptCone(cone_area_ratio=0.92, sleeve_area_ratio=0.9),
            "ccc": CptCone(cone_area_ratio=0.75, sleeve_area_ratio=0.8),
        },
    )


@dataclass
class ExcelData2:
    lab_data: pd.DataFrame
    raw_cpt: pd.DataFrame
    processed_cpt: pd.DataFrame
    cone: dict[str, CptCone]


CURRENT_DIR = os.getcwd()


def get_data_from_excel_calculation_file(file: Files2):
    settings = file.value
    file_path = f"{CURRENT_DIR}/tests/data/calculations/{settings.filename}"

    cpt_raw_data = import_excel_to_dataframe(file_path=file_path, config=settings.raw_cpt)
    lab_data = import_excel_to_dataframe(file_path=file_path, config=settings.lab_data)
    cpt_processed_data = import_excel_to_dataframe(file_path=file_path, config=settings.processed_cpt)

    return ExcelData2(
        raw_cpt=cpt_raw_data,
        lab_data=lab_data,
        processed_cpt=cpt_processed_data,
        cone=settings.cone,
    )
