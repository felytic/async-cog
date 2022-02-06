from struct import unpack
from typing import Literal, Union

from pydantic import PositiveInt

from async_cog.tags.tag import Tag


class NumberTag(Tag):
    value: Union[int, float, None]
    n_values: PositiveInt = 1

    def parse_data(self, byte_order_fmt: Literal["<", ">"]) -> None:
        assert self.data
        (self.value,) = list(unpack(f"{byte_order_fmt}{self.format_str}", self.data))
