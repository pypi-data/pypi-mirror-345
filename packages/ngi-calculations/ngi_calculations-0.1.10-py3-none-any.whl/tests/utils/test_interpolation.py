import numpy as np
import pandas as pd

from ngi_calculations.cpt_correlations.utils.interpolation import interpolate_missing_values

df = pd.DataFrame(
    {
        "depth": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "A": [np.nan, 10.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 90.0, np.nan],
        "B": [0.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 90.0, np.nan],
        "C": [0.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 100.0],
        "D": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 80.0, np.nan, 100.0],
    }
)


class Test_Interpolation:
    def test_interpolate_missing_values__linear_method(self) -> None:
        expected = pd.DataFrame(
            {
                "depth": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
                "A": [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
                "B": [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
                "C": [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
                "D": [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
            }
        )
        result = interpolate_missing_values(df, key_col="depth", mode="linear")
        pd.testing.assert_frame_equal(result, expected)

    def test_interpolate_missing_values__padding_method(self) -> None:
        expected = pd.DataFrame(
            {
                "depth": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
                "A": [np.nan, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 90.0, 90.0],
                "B": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 90.0, 90.0],
                "C": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0],
                "D": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 80.0, 80.0, 100.0],
            }
        )
        result = interpolate_missing_values(df, mode="padding")
        pd.testing.assert_frame_equal(result, expected)
