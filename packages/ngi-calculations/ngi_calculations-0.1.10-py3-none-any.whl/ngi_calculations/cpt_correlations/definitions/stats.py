from dataclasses import dataclass, fields
from enum import Enum
from typing import Optional


class StatsCase(Enum):
    MIN = "min"
    MAX = "max"
    AVG = "avg"
    # Lower part of the data
    P02 = "p_02"
    P05 = "p_05"
    P10 = "p_10"
    P20 = "p_20"
    P30 = "p_30"
    # Upper part of the data
    P70 = "p_70"
    P80 = "p_80"
    P90 = "p_90"
    P95 = "p_95"
    P98 = "p_98"


@dataclass
class Stats:
    P_00: Optional[float] = None
    P_100: Optional[float] = None
    P_50: Optional[float] = None
    # Lower part of the data
    P_02: Optional[float] = None
    P_05: Optional[float] = None
    P_10: Optional[float] = None
    P_20: Optional[float] = None
    P_30: Optional[float] = None
    # Upper part of the data
    P_70: Optional[float] = None
    P_80: Optional[float] = None
    P_90: Optional[float] = None
    P_95: Optional[float] = None
    P_98: Optional[float] = None

    @property
    def min_(self):
        return self.P_00

    @property
    def max_(self):
        return self.P_100

    @property
    def avg_(self):
        return self.P_50

    @property
    def all_equals(self) -> bool:
        return self.max_ == self.min_

    def get_value(self, name: str) -> float:
        getattr(self, name)

    def set_value(self, name: str, value: float) -> None:
        setattr(self, name, value)

    @classmethod
    def list(cls):
        return [field.name for field in fields(cls)]
