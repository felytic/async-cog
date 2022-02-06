from abc import ABC
from struct import calcsize
from typing import Any, Literal, Optional

from pydantic import BaseModel, PositiveInt

from async_cog.tags.tag_code import TagCode
from async_cog.tags.tag_type import TagType


class Tag(BaseModel, ABC):
    code: TagCode
    type: TagType
    n_values: PositiveInt
    data_pointer: Optional[PositiveInt]
    data: Optional[bytes]
    value: Optional[Any]

    def __str__(self) -> str:
        return f"{self.name}: {str(self.value)}"

    @property
    def format_str(self) -> str:
        return f"{self.n_values}{self.type.format}"

    @property
    def data_size(self) -> int:
        return calcsize(self.format_str)

    @property
    def name(self) -> str:
        return self.code.name

    def parse_data(self, byte_order_fmt: Literal["<", ">"]) -> None:
        """
        Parse binary self.data and store values into self.value
        """

        raise NotImplementedError
