from typing import List

from pydantic import BaseModel

from async_cog.tag import Tag


class IFD(BaseModel):
    pointer: int
    n_tags: int
    next_ifd_pointer: int
    tags: List[Tag]
