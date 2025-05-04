from enum import Enum

import pandera as pa
from pandera.dtypes import is_numeric, is_string


class ValueTypeEnum(str, Enum):
    STRING = "string"
    NUMBER = "number"

    @classmethod
    def from_pandera_dtype(cls, dtype: pa.DataType) -> "ValueTypeEnum":
        if is_numeric(dtype):
            return cls.NUMBER
        elif is_string(dtype):
            return cls.STRING
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")
