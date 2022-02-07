from struct import unpack
from typing import List, Literal, Union

from async_cog.tags.tag import Tag


class NumbersTag(Tag):
    value: Union[List[int], List[float], None]

    def parse_data(self, data: bytes, byte_order_fmt: Literal["<", ">"]) -> None:
        self.value = list(unpack(f"{byte_order_fmt}{self.format_str}", data))
