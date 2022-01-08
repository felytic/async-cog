from typing import List, Optional

from PIL.TiffTags import TAGS_V2, TagInfo
from pydantic import BaseModel, validator


class Tag(BaseModel):
    code: int
    type: int
    n_values: int
    pointer: int
    data: Optional[bytes]

    @validator("code")
    def validate_tag_supported(cls, code: int) -> int:
        if code not in TAGS_V2:
            raise ValueError(f"Tag with code {code} is not supported")

        return code

    @property
    def tag_info(self) -> TagInfo:
        return TAGS_V2.get(self.code)

    @property
    def name(self) -> str:
        return str(self.tag_info.name)

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
