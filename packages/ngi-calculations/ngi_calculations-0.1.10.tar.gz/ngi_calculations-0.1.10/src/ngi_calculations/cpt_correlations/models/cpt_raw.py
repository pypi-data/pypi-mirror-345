import pandas as pd
from pydantic import BaseModel, Field, field_validator

from ngi_calculations.cpt_correlations.models.cpt_cone import CptCone
from ngi_calculations.cpt_correlations.utils.models import CustomBaseModel


class RawCPTColumns(BaseModel):
    depth: str = "depth"
    qc: str = "qc"
    fs: str = "fs"
    u2: str = "u2"
    penetration_rate: str = "penetration_rate"
    penetration_force: str = "penetration_force"
    # conductivity: str = "conductivity"
    temperature: str = "temperature"
    tilt: str = "tilt"

    @property
    def all(self):
        return [
            self.depth,
            self.qc,
            self.fs,
            self.u2,
            self.penetration_rate,
            self.penetration_force,
            # self.conductivity,
            self.temperature,
            self.tilt,
        ]


class RawCPT(CustomBaseModel):
    data: pd.DataFrame = Field(..., description="Pandas DataFrame containing raw CPT data")
    columns: RawCPTColumns = RawCPTColumns()
    cone: dict[str, CptCone] | None = None

    @field_validator("data")
    def validate_data(cls, value):
        return cls.check_type(value, pd.DataFrame)
