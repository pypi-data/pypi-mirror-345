from typing import Literal

from pydantic.main import BaseModel


class CptProcessOptions(BaseModel):
    elevation: float = 0
    shift_depth: float = 0.0  # Shift CPT depth (in m, negative value shifts upwards)
    adjust_depth_tilt: bool = False  # Adjust depth due to tilt
    compensate_atm_pressure: bool = False
    interpolation_mode: Literal["linear", "padding"] = "linear"
    cpt_identifier: str = "method_id"
