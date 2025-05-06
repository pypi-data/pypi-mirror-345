import pytest
from tests.data.faker_cpt import fake_cpt, fake_lab_profile_data

from ngi_calculations.cpt_correlations.definitions.geo import GEO
from ngi_calculations.cpt_correlations.definitions.physics import PhysicParameters as PHY
from ngi_calculations.cpt_correlations.methods.cpt_process.calculations import CPTProcessCalculation
from ngi_calculations.cpt_correlations.models.cpt_raw import RawCPT
from ngi_calculations.cpt_correlations.models.lab_data import LabData


@pytest.fixture
def simple_data() -> None:
    raw_cpt = RawCPT(data=fake_cpt(step=1, depth_range=(0, 10), qc_range=(0, 10)))
    lab_data = LabData(data=fake_lab_profile_data())
    cpt_process = CPTProcessCalculation(raw_cpt=raw_cpt, lab_data=lab_data)
    cpt_process.calculate()
    return cpt_process


class TestProcessCPT_Calculation_Simple:
    def test_correct_instantiation(self, simple_data) -> None:
        assert simple_data.raw_cpt.data["qc"][0] == 0
        assert simple_data.data["qc"][0] == 0

    def test_shift_depth(self, simple_data) -> None:
        simple_data.options.shift_depth = 0
        simple_data.calculate()
        assert simple_data.data[GEO.depth.key].equals(simple_data.data[GEO.depth_raw.key])

        simple_data.options.shift_depth = 1
        simple_data.calculate()
        assert simple_data.data[GEO.depth.key].equals(simple_data.data[GEO.depth_raw.key] + 1)

        simple_data.options.shift_depth = -1
        simple_data.calculate()
        assert simple_data.data[GEO.depth.key].equals(simple_data.data[GEO.depth_raw.key] - 1)

        simple_data.options.shift_depth = -2
        simple_data.calculate()
        assert simple_data.data[GEO.depth.key].equals(simple_data.data[GEO.depth_raw.key] - 2)

        simple_data.options.shift_depth = 0
        simple_data.calculate()
        assert simple_data.data[GEO.depth.key].equals(simple_data.data[GEO.depth_raw.key])

    def test_compensate_patm(self, simple_data):
        simple_data.options.compensate_atm_pressure = True
        simple_data.calculate()
        assert simple_data.data[GEO.u2.key].equals(simple_data.data[GEO.u2_raw.key] - PHY.P_atm)

        simple_data.options.compensate_atm_pressure = False
        simple_data.calculate()
        assert simple_data.data[GEO.u2.key].equals(simple_data.data[GEO.u2_raw.key])
