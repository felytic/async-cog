from struct import calcsize
from typing import List, Optional

from pydantic import BaseModel, validator

# https://docs.python.org/3/library/struct.html#format-characters
TAG_TYPES = {
    1: "B",  # BYTE
    2: "c",  # ASCII
    3: "H",  # SHORT
    4: "I",  # LONG
    # FIXME In TIFF format, a RATIONAL value is a fractional value
    # represented by the ratio of two unsigned 4-byte integers.
    5: "Q",  # RATIONAL
    6: "b",  # SBYTE
    7: "c",  # UNDEFINED
    8: "h",  # SSHORT
    9: "i",  # SLONG
    # FIXME same for signed RATIONAL
    10: "q",  # SRATIONAL
    11: "f",  # FLOAT
    12: "d",  # DOUBLE
    16: "Q",  # LONG8
}


class Tag(BaseModel):
    code: int
    type: int
    n_values: int
    pointer: int
    data: Optional[bytes]

    @validator("type")
    def validate_type(cls, type_code: int) -> int:
        if type_code not in TAG_TYPES:
            raise ValueError(f"Tag with type {type_code} is not supported")

        return type_code

    @property
    def format(self) -> str:
        return f"{self.n_values}{TAG_TYPES[self.type]}"

    @property
    def data_size(self) -> int:
        return calcsize(self.format)


class IFD(BaseModel):
    offset: int
    n_tags: int
    next_ifd_pointer: int
    tags: List[Tag]
