from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicParameters:
    P_atm: float = 100
