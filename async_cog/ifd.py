from typing import Any, Dict, List

from pydantic import BaseModel

from async_cog.tag import Tag


class IFD(BaseModel):
    pointer: int
    n_tags: int
    next_ifd_pointer: int
    tags: List[Tag]

    def to_dict(self) -> Dict[str, Any]:
        return {
            tag.name: tag.value for tag in self.tags if not isinstance(tag.value, bytes)
        }
