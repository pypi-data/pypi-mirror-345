from pydantic import BaseModel, field_validator
import pandas as pd

from ngi_calculations.cpt_correlations.utils.models import CustomBaseModel


class LabDataColumns(BaseModel):
    depth: str = "depth"
    uw: str = "uw"


class LabData(CustomBaseModel):
    data: pd.DataFrame
    columns: LabDataColumns = LabDataColumns()

    @field_validator("data")
    def validate_data(cls, value):
        return cls.check_type(value, pd.DataFrame)
