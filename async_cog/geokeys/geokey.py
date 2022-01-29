from typing import Any, Optional

from pydantic import BaseModel, NonNegativeInt

from async_cog.geokeys.geokey_code import GeoKeyCode
from async_cog.tags.tag_code import TagCode


class GeoKey(BaseModel):
    code: GeoKeyCode
    tag_code: Optional[TagCode]
    length: NonNegativeInt
    value: Optional[Any]
    offset: Optional[NonNegativeInt]

    def __str__(self) -> str:
        return f"{self.name}: {str(self.value)}"

    @property
    def name(self) -> str:
        return self.code.name
