from typing import Any, Optional

from pydantic import BaseModel

from async_cog.geokeys.geokey_code import GeoKeyCode


class GeoKey(BaseModel):
    code: GeoKeyCode
    value: Optional[Any]

    def __str__(self) -> str:
        return f"{self.name}: {str(self.value)}"

    @property
    def name(self) -> str:
        return self.code.name
