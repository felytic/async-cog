from typing import Literal, Optional

from async_cog.tags.tag import Tag
from async_cog.tags.tag_type import TagType


class StringTag(Tag):
    value: Optional[str]
    type = TagType(2)

    def parse_data(self, byte_order_fmt: Literal["<", ">"]) -> None:
        assert self.data
        self.value = self.data.decode()
