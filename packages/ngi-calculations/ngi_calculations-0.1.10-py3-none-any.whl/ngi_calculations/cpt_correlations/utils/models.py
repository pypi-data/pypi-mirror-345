from typing import Any, Type

from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def check_type(cls, value: Any, expected_type: Type) -> Any:
        if not isinstance(value, expected_type):
            raise ValueError(f"value must be of type {expected_type.__name__}")
        return value
