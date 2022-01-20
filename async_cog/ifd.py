from typing import Any, Dict

from pydantic import BaseModel

from async_cog.tag import Tag


class IFD(BaseModel):
    pointer: int
    n_tags: int
    next_ifd_pointer: int
    tags: Dict[str, Tag]

    def to_dict(self) -> Dict[str, Any]:
        return {
            tag.name: tag.value
            for tag in self.tags.values()
            if not isinstance(tag.value, bytes)
        }

    def __getitem__(self, key: str) -> Any:
        return self.tags[key].value

    def __setitem__(self, key: str, tag: Tag) -> None:
        assert tag.name == key
        self.tags[key] = tag
