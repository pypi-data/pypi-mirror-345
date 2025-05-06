from typing import Tuple

import numpy as np
import pandas as pd


def fake_cpt(
    step: float,
    depth_range: Tuple[float, float] = (0.0, 1.0),
    qc_range: Tuple[float, float] = (0.0, 1.0),
    u2_range: Tuple[float, float] = (0.0, 1.0),
    fs_range: Tuple[float, float] = (0.0, 1.0),
    temperature_range: Tuple[float, float] = (0.0, 1.0),
    penetration_force: Tuple[float, float] = (0.0, 1.0),
    penetration_rate: Tuple[float, float] = (0.0, 1.0),
    tilt: Tuple[float, float] = (0.0, 1.0),
    conductivity: Tuple[float, float] = (0.0, 1.0),
):
    # Check if step is lower than the stop value
    if step >= depth_range[1]:
        raise ValueError("Step should be lower than the stop value in depth_range.")
    # Create an empty dataframe
    df = pd.DataFrame()
    # Generate the depth column
    depth = [*np.arange(depth_range[0], depth_range[1], step), depth_range[1]]
    df["depth"] = depth

    # Define the column names and their corresponding ranges
    columns = [
        "qc",
        "u2",
        "fs",
        "temperature",
        "penetration_force",
        "penetration_rate",
        "tilt",
        "conductivity",
    ]
    ranges = [
        qc_range,
        u2_range,
        fs_range,
        temperature_range,
        penetration_force,
        penetration_rate,
        tilt,
        conductivity,
    ]

    # Loop through each column
    for column, column_range in zip(columns, ranges):
        # Generate the column values
        values = np.full(len(depth), np.nan)
        values[0] = column_range[0]
        values[-1] = column_range[-1]
        df[column] = values
    df = df.interpolate(method="linear", axis=0)
    # cast all columns to float
    df = df.astype(float)

    return df


def fake_lab_profile_data():
    lab_profile = pd.DataFrame()
    lab_profile["depth"] = np.arange(0, 10, 1)
    lab_profile["u0"] = np.arange(0, 10, 1)
    lab_profile["wc"] = np.arange(0, 10, 1)
    lab_profile["uw"] = np.arange(0, 10, 1)
    lab_profile["St"] = np.arange(0, 10, 1)
    lab_profile["Ip"] = np.arange(0, 10, 1)
    return lab_profile


# LAB_PROFILE_SPEC = [
#     dict(name="u0_profile", type="multiplier-u0", x_key="u0", multiplier=10, default_value=10, initial_value=0),
#     dict(name="wc_profile", type="average", x_key="wc", watch_keys=["wc"], default_value=30),
#     dict(name="uw_profile", type="average", x_key="uw", watch_keys=["uw"], default_value=18),
#     dict(name="St_profile", type="average", x_key="St", watch_keys=["St_Fc"], default_value=10),
#     dict(name="Ip_profile", type="average", x_key="Ip", watch_keys=["Ip"], default_value=10),
# ]
#
# test = fake_cpt(step=2, depth_range=(0, 10), qc_range=(0, 10))
# print(test)
