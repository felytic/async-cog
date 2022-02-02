from __future__ import annotations

from typing import Any, Iterator


class TagType(int):
    format: str

    @classmethod
    def __get_validators__(cls) -> Iterator[Any]:
        yield cls.validate

    @classmethod
    def validate(cls, type_code: int) -> TagType:
        return cls(type_code)

    def __init__(self, type_code: int):
        assert isinstance(type_code, int)

        if type_code not in TAG_TYPES:
            raise ValueError(f"Tag with type {type_code} is not supported")

        self.format = TAG_TYPES[type_code]


# https://docs.python.org/3/library/struct.html#format-characters
TAG_TYPES = {
    1: "B",  # BYTE (1 byte integer)
    2: "s",  # ASCII
    3: "H",  # SHORT
    4: "I",  # LONG
    # In TIFF format, a RATIONAL value is a fractional value
    # represented by the ratio of two unsigned 4-byte integers.
    5: "Q",  # FRACTION
    6: "b",  # SBYTE (1 byte integer)
    7: "s",  # UNDEFINED (bytes)
    8: "h",  # SSHORT
    9: "i",  # SLONG
    # same for signed RATIONAL
    10: "q",  # SIGNED FRACTION
    11: "f",  # FLOAT
    12: "d",  # DOUBLE
    16: "Q",  # LONG8
}
