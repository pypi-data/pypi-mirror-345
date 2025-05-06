from typing import Literal, Union

type_float_or_int = Union[float, int]
type_auto_or_int = Union[Literal["auto"], int]
type_flex = Literal["fixed", "shrink", "grow", "adapt"]
