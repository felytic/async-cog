from struct import calcsize, unpack
from typing import Any, Literal, Optional

from pydantic import BaseModel, PositiveInt

from async_cog.geokeys import GeoKey
from async_cog.tags.tag_code import TagCode
from async_cog.tags.tag_type import TagType


class Tag(BaseModel):
    code: TagCode
    type: TagType
    n_values: PositiveInt
    data_pointer: Optional[PositiveInt]
    data: Optional[bytes]
    values: Optional[Any]

    def __str__(self) -> str:
        return f"{self.name}: {str(self.value)}"

    @property
    def format_str(self) -> str:
        return f"{self.n_values}{self.type.format}"

    @property
    def data_size(self) -> int:
        return calcsize(self.format_str)

    @property
    def name(self) -> str:
        return self.code.name

    @property
    def value(self) -> Any:
        if self.values:
            if self.name == "GeoKeyDirectoryTag":
                return {item.name: item.value for item in self.values}

            return self.values

        return self.data

    def parse_data(self, byte_order_fmt: Literal["<", ">"]) -> None:
        """
        Parse binary self.data and store values into self.values
        """

        if self.data is None:
            return

        self._parse(byte_order_fmt)

        if self.name == "GeoKeyDirectoryTag":
            self._parse_geokeys()

    def _parse(self, byte_order_fmt: Literal["<", ">"]) -> None:
        """
        Parse values from binary self.data according to self.format_str
        """

        assert self.data
        self.values = list(unpack(f"{byte_order_fmt}{self.format_str}", self.data))

    def _parse_geokeys(self) -> None:
        """
        GeoKey structure (array of size 4 * n):
        +---------+-------------+----------------+--------+
        | version |    revision | minor_revision | keys_n |
        +---------+-------------+----------------+--------+
        |   . . . |       . . . |          . . . |  . . . |
        +---------+-------------+----------------+--------+
        |    code |    tag_code |         length |  value |
        +---------+-------------+----------------+--------+
        |   . . . |       . . . |          . . . |  . . . |
        +---------+-------------+----------------+--------+

        If tag_code != 0 then values are in tag with "tag_code" code on position "value"

        svn.osgeo.org/metacrs/geotiff/trunk/geotiff/html/usgs_geotiff.html#hdr%2023
        """
        if self.values and len(self.values) >= 4:
            version, _, _, keys_n = self.values[:4]
            assert version == 1

            geo_keys = []

            for i in range(1, keys_n + 1):
                code, tag_code, length, value = self.values[4 * i : 4 * (i + 1)]
                offset = None

                if tag_code != 0:
                    offset = value
                    value = None

                geo_key = GeoKey(
                    code=code,
                    tag_code=tag_code,
                    length=length,
                    value=value,
                    offset=offset,
                )

                geo_keys.append(geo_key)

            self.values = geo_keys
