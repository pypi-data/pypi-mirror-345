from pydantic import BaseModel


class CptCone(BaseModel):
    cone_area_ratio: float = 1.0
    sleeve_area_ratio: float = 1.0
