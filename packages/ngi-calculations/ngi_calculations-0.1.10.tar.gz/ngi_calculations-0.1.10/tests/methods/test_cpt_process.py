import pandas as pd
import pytest

from ngi_calculations.cpt_correlations.definitions.geo import GEO


def calc_assert(
    results: pd.DataFrame,
    expected: pd.DataFrame,
    key: str,
    rtol: float = 1e-2,
    atol: float = 1e-4,
    log: bool = False,
) -> None:
    """Helper function to compare a series from the analysis_from_excel with the expected series"""

    if log:
        print("key", key)
        print("results from the calculations\n", results[key].head(10))
        print("expected values\n", expected[key].head(10))
        print("results from the calculations\n", results[key].tail(10))
        print("expected values\n", expected[key].tail(10))

    pd.testing.assert_series_equal(
        results[key], expected[key], check_index=False, check_exact=False, atol=atol, rtol=rtol
    )


class TestCPTProcessCalculation:
    @pytest.fixture(scope="class")
    def processed_data(self, analysis_from_excel):
        analysis_from_excel.processor.calculate()
        return {"results": analysis_from_excel.processor.data, "expected": analysis_from_excel.expected}

    @pytest.mark.parametrize(
        "key",
        [
            "method_id",
            GEO.depth.key,
            GEO.qc.key,
            GEO.fs.key,
            GEO.tilt.key,
            GEO.temperature.key,
            GEO.penetration_rate.key,
            GEO.penetration_force.key,
        ],
    )
    def test_raw_data(self, processed_data, key):
        calc_assert(processed_data["results"], processed_data["expected"], key)

    @pytest.mark.parametrize(
        "key",
        [
            GEO.depth.key,
            GEO.wc.key,
            GEO.WP.key,
            GEO.LL.key,
            GEO.Ip.key,
            GEO.St.key,
            GEO.uw.key,
            GEO.qc.key,
            GEO.fs.key,
            GEO.u2.key,
            GEO.u0.key,
            GEO.cone_area_ratio.key,
            GEO.sleeve_area_ratio.key,
            GEO.sigVtTotal.key,
            GEO.sigVtEff.key,
            GEO.u_delta.key,
            GEO.u_delta_norm.key,
            GEO.qt.key,
            GEO.qn.key,
            GEO.Qt.key,
            GEO.Bq.key,
            GEO.Rf.key,
            GEO.Fr.key,
            GEO.Ic.key,
            GEO.n.key,
            GEO.Qtn.key,
            GEO.Icn.key,
        ],
    )
    def test_calculation(self, processed_data, key):
        calc_assert(processed_data["results"], processed_data["expected"], key)
