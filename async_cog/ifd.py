from typing import List

from PIL.TiffTags import lookup
from pydantic import BaseModel


class Tag(BaseModel):
    code: int
    type: int
    n_values: int
    pointer: int

    @property
    def name(self) -> str:
        tag_info = lookup(self.code)
        return str(tag_info.name)

    def __repr__(self) -> str:
        return (
            f"{self.name}(code: {self.code}, type: {self.type}, "
            f"n_values: {self.n_values}, pointer: {self.pointer})"
        )


class IFD(BaseModel):
    offset: int
    n_tags: int
    next_ifd_pointer: int
    tags: List[Tag]
