from math import log

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

from ngi_calculations.cpt_correlations.config import MIN_CPT_ALLOWED_STEP
from ngi_calculations.cpt_correlations.definitions.geo import GEO
from ngi_calculations.cpt_correlations.definitions.physics import PhysicParameters as PHY
from ngi_calculations.cpt_correlations.methods.cpt_process.options import CptProcessOptions
from ngi_calculations.cpt_correlations.models.cpt_cone import CptCone
from ngi_calculations.cpt_correlations.models.cpt_raw import RawCPT
from ngi_calculations.cpt_correlations.models.lab_data import LabData
from ngi_calculations.cpt_correlations.utils.interpolation import interpolate_missing_values
from ngi_calculations.cpt_correlations.utils.perf_log import measure, track_execution


class CPTProcessCalculation:
    raw_cpt: RawCPT
    lab_data: LabData
    options: CptProcessOptions

    data: DataFrame  # = param.DataFrame(doc="CPT processed data")

    step: float  # = param.Number(default=0.01)
    depth_raw: any  # = param.Array()
    min_depth: float  # = param.Number()
    max_depth: float  # = param.Number()

    def __init__(self, raw_cpt: RawCPT, lab_data: LabData, options: CptProcessOptions = CptProcessOptions()) -> None:
        self.raw_cpt = raw_cpt
        self.lab_data = lab_data
        self.options = options

    @measure("ProcessCPT_Calculation", log_time=False, log_child=False)
    @track_execution
    def calculate(self):
        """Calculation pipeline order"""

        self._set_initial_data()
        self._set_depth_boundaries()
        self._guess_step()
        self._add_missing_depths()
        self._shift_depth_for_tilt()
        self._shift_depth()
        self._compensate_atmospheric_pressure()
        self._integrate_lab_profile()
        self._total_vertical_stress()
        self._effective_vertical_stress()
        self._differential_pressure()
        self._normalized_differential_pressure()
        self._elevation()
        self._set_cone_info()
        self._total_cone_resistance()
        self._net_cone_resistance()
        self._normalized_cone_resistance()
        self._normalized_pressure()
        self._friction_ratio()
        self._normalized_friction_ratio()
        self._soil_behavior_index()
        self._soil_behavior_exponent()
        self._normalized_cone_resistance_with_n()
        self._normalized_soil_behavior_index()
        self._filter_data()

    def _set_initial_data(self):
        self.data = self.raw_cpt.data.copy()
        self.data[GEO.u2_raw.key] = self.data[GEO.u2.key]
        self.data[GEO.depth_raw.key] = self.data[GEO.depth.key]
        self.depth_raw = self.data[GEO.depth.key].values

    def _set_depth_boundaries(self):
        depth_key = GEO.depth.key
        self.min_depth = self.data[depth_key].iloc[0]
        self.max_depth = self.data[depth_key].iloc[-1]

    def _guess_step(self):
        step = np.diff(self.data[GEO.depth_raw.key])
        step = np.around(step, decimals=2)
        min_step = np.amin(step)  # Guess the step before inserting the first zero value as it will falsify the guess
        self.step = min_step
        step = np.insert(step, 0, 0.0, axis=0)
        self.data["step"] = step

    def _add_missing_depths(self):
        depth_key = GEO.depth_raw.key
        min_depth = self.data[depth_key].iloc[0]
        max_depth = self.data[depth_key].iloc[-1]
        step = self.step

        # only add missing if the step is not lower than a minimal threshold (to avoid adding incorrect steps)
        if step > MIN_CPT_ALLOWED_STEP:
            # logger.info("ProcessCPT - adding missing depths")

            df_stepped_depth = pd.DataFrame({depth_key: np.arange(start=min_depth, stop=max_depth, step=step)})
            df_stepped_depth["step"] = self.step

            self.data.rename(columns={"step": "step_raw"})

            df = (
                pd.concat([self.data, df_stepped_depth])
                .round(decimals={depth_key: 2})
                .drop_duplicates(subset=depth_key, keep="first")
                .sort_values(by=depth_key)
                .reset_index(drop=True)
            )

            df[GEO.depth.key] = df[depth_key]

            self.data = df
        else:
            pass
            # logger.info(f"ProcessCPT - will not add missing depths as step={step}")

    def _shift_depth_for_tilt(self):
        """Correct for tilt. Does not impact the rest of the calculation. Only used as a visual clue."""
        self.data[GEO.depth_tilt.key] = self.data[GEO.depth_raw.key]
        # if self.cpt_data.options.adjust_depth_tilt:
        #     depth_diff = np.diff(self.df[GEO.depth_raw.key])
        #     depth_diff = np.insert(depth_diff, 0, 0.0, axis=0)
        #     depth_ = depth_diff * np.cos(np.radians(self.df[GEO.tilt.key]))
        #     self.df[GEO.depth_tilt.key] = depth_
        #     self.df[GEO.depth_tilt.key].iloc[0] = self.df[GEO.depth.key].iloc[0]
        #     self.df[GEO.depth_tilt.key] = self.df[GEO.depth_tilt.key].cumsum()
        #     self.df[GEO.depth_tilt.key] = self.df[GEO.depth_tilt.key].round(decimals=2)
        # else:
        #     # Restore the original depths
        #     self.df[GEO.depth_tilt.key] = self.df[GEO.depth_raw.key]

    def _shift_depth(self):
        if self.options.shift_depth != 0:
            self.data[GEO.depth.key] = self.data[GEO.depth.key] + self.options.shift_depth
        else:
            # Restore the original depths
            self.data[GEO.depth.key] = self.data[GEO.depth_raw.key]

        # Update the depth boundaries
        self._set_depth_boundaries()

    def _compensate_atmospheric_pressure(self):
        if self.options.compensate_atm_pressure:
            self.data[GEO.u2.key] = self.data[GEO.u2_raw.key] - PHY.P_atm
        else:
            self.data[GEO.u2.key] = self.data[GEO.u2_raw.key]

    def _integrate_lab_profile(self):
        """Method to linearize the lab profiles to the CPT depth and interpolate missing values"""

        _df = self.data.copy()
        # Alias to the enum key
        depth = GEO.depth.key

        # # Minimum/Maximum depth of the CPT, should not interpolate beyond
        # min_depth = _df.iloc[0][depth]
        # max_depth = _df.iloc[-1][depth]

        # Get the lab profiles
        lab_df = self.lab_data.data

        # Drop the existing lab columns if they already exist in the Dataframe
        # This to avoid the issue where the columns exist twice with an appended string after merge
        # (e.g. u0 --> u0_x and u0_y)
        lab_cols = lab_df.columns.values.tolist()
        lab_cols = [col for col in lab_cols if col != "depth"]
        _df = _df.drop([x for x in lab_cols if x in _df.columns], axis=1)

        # Merge the two Dataframes
        # Create a type dictionary for all columns
        types_dict = {col: np.float64 for col in _df.columns if col != self.options.cpt_identifier and col != depth}
        # Add depth type if needed
        types_dict[depth] = np.float64
        # Apply types
        _df = _df.astype(types_dict)

        # _df.astype(np.float64, copy=False)
        _df = pd.merge(_df, lab_df, on=depth, how="outer")
        _df.sort_values(by=depth, inplace=True)
        _df.set_index(depth, drop=False, inplace=True)

        # Interpolate the missing values.
        _df = interpolate_missing_values(
            _df, key_col=depth, col_list=[c for c in lab_cols if c != "u0"], mode=self.options.interpolation_mode
        )

        # Handle u0 differently as it should always be interpolated linearly
        _df = interpolate_missing_values(_df, key_col=depth, col_list=["u0"], mode="linear")

        # # Prevent values for certain lab profiles to go below zero
        # _df[GEO.u0.key] = _df[GEO.u0.key].clip(lower=0.0)

        # Prevent values f to go below zero
        for col in lab_cols:
            _df[col] = _df[col].clip(lower=0.0)

        # Return only the values in the CPT range (interpolated values outside the CPT range are not valid)
        # _df = _df.loc[(_df[depth] >= min_depth) & (_df[depth] <= max_depth)]

        # Drop the depth as index as it is incompatible with the Tabulator implementation and return the new Dataframe
        _df.reset_index(inplace=True, drop=True)

        self.data = _df

    def _total_vertical_stress(self):
        # Get the depth difference
        _depth = self.data[GEO.depth.key].values
        _depth_diff = np.diff(_depth)
        _depth_diff = np.insert(_depth_diff, 0, _depth[0])

        def moving_average(x, w):
            return np.convolve(x, np.ones(w), "valid") / w

        # Get the mean unit weight over two consecutive depth
        _uw = self.data[GEO.uw.key].values
        _uw_mean = moving_average(_uw, 2)
        _uw_mean = np.insert(_uw_mean, 0, _uw[0])

        # Compute the total vertical stress
        _sigVtTotal = np.cumsum(_uw_mean * _depth_diff)
        self.data[GEO.sigVtTotal.key] = _sigVtTotal

    def _effective_vertical_stress(self):
        self.data[GEO.sigVtEff.key] = self.data[GEO.sigVtTotal.key] - self.data[GEO.u0.key]
        self.data[GEO.sigVtEff.key] = self.data[GEO.sigVtEff.key].clip(lower=0.0)
        # self.df[GEO.sigVtEff.key] = self.df[GEO.sigVtEff.key].clip(lower=0.0).round(decimals=GEO.sigVtEff.precision)

    def _differential_pressure(self):
        self.data[GEO.u_delta.key] = self.data[GEO.u2.key] - self.data[GEO.u0.key]

    def _normalized_differential_pressure(self):
        normU = np.where(
            self.data[GEO.sigVtEff.key] <= 0,
            0,
            self.data[GEO.u_delta.key] / self.data[GEO.sigVtEff.key],
        )
        self.data[GEO.u_delta_norm.key] = normU
        # self.df[GEO.u_delta_norm.key] = self.df[GEO.u_delta_norm.key] / self.df[GEO.sigVtEff.key]

    def _elevation(self):
        # TODO: Where to make available the self.options.elevation?
        self.data[GEO.elevation.key] = self.options.elevation - self.data[GEO.depth.key]

    def _set_cone_info(self):
        if self.options.cpt_identifier in self.data.columns:
            # Create a function to map each identifier to the corresponding cone area ratio value
            def get_cone_area_ratio(identifier):
                cone = self.raw_cpt.cone.get(identifier)
                # Return the numeric cone_area_ratio attribute, not the entire CptCone object
                return cone.cone_area_ratio if cone else CptCone().cone_area_ratio

            # Apply the function to each row's identifier
            self.data[GEO.cone_area_ratio.key] = self.data[self.options.cpt_identifier].apply(get_cone_area_ratio)
        else:
            # If the identifier column doesn't exist, use the default value
            self.data[GEO.cone_area_ratio.key] = CptCone().cone_area_ratio

        # Do the same for sleeve_area_ratio
        if self.options.cpt_identifier in self.data.columns:

            def get_sleeve_area_ratio(identifier):
                cone = self.raw_cpt.cone.get(identifier)
                # Return the numeric sleeve_area_ratio attribute, not the entire CptCone object
                return cone.sleeve_area_ratio if cone else CptCone().sleeve_area_ratio

            self.data[GEO.sleeve_area_ratio.key] = self.data[self.options.cpt_identifier].apply(get_sleeve_area_ratio)
        else:
            self.data[GEO.sleeve_area_ratio.key] = CptCone().sleeve_area_ratio

    def _total_cone_resistance(self):
        self.data[GEO.qt.key] = (
            1000 * self.data[GEO.qc.key] + self.data[GEO.u2.key] * (1 - self.data[GEO.cone_area_ratio.key])
        ) / 1000

    def _net_cone_resistance(self):
        self.data[GEO.qn.key] = self.data[GEO.qt.key] - self.data[GEO.sigVtTotal.key] / 1000

    def _normalized_cone_resistance(self):
        self.data[GEO.Qt.key] = (1000 * self.data[GEO.qt.key] - self.data[GEO.sigVtTotal.key]) / self.data[
            GEO.sigVtEff.key
        ]

    def _normalized_pressure(self):
        self.data[GEO.Bq.key] = (self.data[GEO.u2.key] - self.data[GEO.u0.key]) / (
            1000 * self.data[GEO.qt.key] - self.data[GEO.sigVtTotal.key]
        )

    def _friction_ratio(self):
        self.data[GEO.Rf.key] = 100 * self.data[GEO.fs.key] / (1000 * self.data[GEO.qc.key])

    def _normalized_friction_ratio(self):
        self.data[GEO.Fr.key] = (
            100 * self.data[GEO.fs.key] / (1000 * self.data[GEO.qt.key] - self.data[GEO.sigVtTotal.key])
        )

    def _soil_behavior_index(self):
        self.data[GEO.Ic.key] = np.sqrt(
            (3.47 - np.log10(self.data[GEO.Qt.key])) ** 2.0 + (np.log10(self.data[GEO.Fr.key]) + 1.22) ** 2.0
        )

    def _soil_behavior_exponent(self):
        self.data[GEO.n.key] = 0.381 * self.data[GEO.Ic.key] + 0.05 * (self.data[GEO.sigVtEff.key] / PHY.P_atm) - 0.15
        self.data[GEO.n.key] = self.data[GEO.n.key].clip(upper=1.0)  # any value > 1.0 will be clipped to 1.0

    def _normalized_cone_resistance_with_n(self):
        self.data[GEO.Qtn.key] = self.data[GEO.Qt.key] * (PHY.P_atm / self.data[GEO.sigVtEff.key]) ** (
            self.data[GEO.n.key] - 1
        )

    def _normalized_soil_behavior_index(self):
        self.data[GEO.Icn.key] = np.sqrt(
            (3.47 - np.log(self.data[GEO.Qtn.key]) / log(10)) ** 2.0
            + (np.log(self.data[GEO.Fr.key]) / log(10) + 1.22) ** 2.0
        )

    def _filter_data(self):
        depth = GEO.depth.key
        self.data = self.data.loc[(self.data[depth] >= self.min_depth) & (self.data[depth] <= self.max_depth)]

    @property
    def results(self):
        return self.data.reset_index(inplace=False, drop=True)
