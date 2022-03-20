from struct import unpack
from typing import Literal, Union

from pydantic import PositiveInt

from async_cog.tags.tag import Tag


class NumberTag(Tag):
    value: Union[int, float, None]
    length: PositiveInt = 1

    def parse_data(self, data: bytes, byte_order_fmt: Literal["<", ">"]) -> None:
        (self.value,) = unpack(f"{byte_order_fmt}{self.format_str}", data)
