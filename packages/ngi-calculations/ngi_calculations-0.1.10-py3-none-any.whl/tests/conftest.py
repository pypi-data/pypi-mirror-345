from dataclasses import dataclass
from typing import Callable

import pandas as pd
import pytest

from ngi_calculations.cpt_correlations.methods.cpt_process.calculations import CPTProcessCalculation
from ngi_calculations.cpt_correlations.models.cpt_raw import RawCPT
from ngi_calculations.cpt_correlations.models.lab_data import LabData
from tests.data.calculation_data import Files2, get_data_from_excel_calculation_file


def dict_parametrize(data, **kwargs) -> Callable:
    args = list(list(data.values())[0].keys())
    formatted_data = [[item[a] for a in args] for item in data.values()]
    ids = list(data.keys())
    return pytest.mark.parametrize(args, formatted_data, ids=ids, **kwargs)


@dataclass
class FullCase:
    # cpt_data: CptData
    raw_cpt: RawCPT
    processor: CPTProcessCalculation
    expected: pd.DataFrame


@pytest.fixture(params=[Files2.testA], scope="session")
def analysis_from_excel(request):
    excel_data = get_data_from_excel_calculation_file(request.param)
    raw_cpt = RawCPT(data=excel_data.raw_cpt, cone=excel_data.cone)
    lab_data = LabData(data=excel_data.lab_data)
    processor = CPTProcessCalculation(raw_cpt=raw_cpt, lab_data=lab_data)
    return FullCase(raw_cpt=raw_cpt, processor=processor, expected=excel_data.processed_cpt)


def pytest_configure():
    pytest.dict_parametrize = dict_parametrize
    pytest.FullCase = FullCase
