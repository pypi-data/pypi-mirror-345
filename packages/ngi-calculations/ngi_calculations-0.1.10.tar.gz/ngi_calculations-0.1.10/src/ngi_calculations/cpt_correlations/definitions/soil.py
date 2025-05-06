from enum import Enum


class SoilTypes(Enum):
    CLAY = "clay"
    SAND = "sand"
    SILT = "silt"
    ROCK = "rock"
    SKIP = "skip"


soil_list = [e.value for e in SoilTypes]
