from typing import Literal, Optional

from async_cog.tags.tag import Tag
from async_cog.tags.tag_type import TagType


class BytesTag(Tag):
    values: Optional[bytes]
    type = TagType(7)

    def parse_data(self, byte_order_fmt: Literal["<", ">"]) -> None:
        self.values = self.data
