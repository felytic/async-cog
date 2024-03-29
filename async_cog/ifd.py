from math import ceil
from typing import Any, Dict, Union

import numpy as np
from pydantic import BaseModel, NonNegativeInt

from async_cog.geokeys import GeoKey
from async_cog.tags import Tag
from async_cog.tags.tag_code import GEOKEY_TAGS, TagCode


class IFD(BaseModel):
    pointer: NonNegativeInt
    n_tags: NonNegativeInt
    next_ifd_pointer: NonNegativeInt
    tags: Dict[str, Tag] = {}
    geokeys: Dict[str, GeoKey] = {}

    def __getitem__(self, key: str) -> Any:
        if key in self.geokeys:
            return self.geokeys[key].value

        return self.tags[key].value

    def get(self, key: str, default: Any = None) -> Any:
        if key in self:
            return self[key]

        return default

    def __setitem__(self, key: str, tag_or_geokey: Union[Tag, GeoKey]) -> None:
        assert tag_or_geokey.name == key

        if isinstance(tag_or_geokey, Tag):
            self.tags[key] = tag_or_geokey

        if isinstance(tag_or_geokey, GeoKey):
            self.geokeys[key] = tag_or_geokey

    def __contains__(self, key: str) -> bool:
        return key in self.tags or key in self.geokeys

    def to_dict(self) -> Dict[str, Any]:
        tags = {
            tag.name: tag.value
            for tag in self.tags.values()
            if not isinstance(tag.value, bytes) and tag.code not in GEOKEY_TAGS
        }
        geokeys = {geokey.name: geokey.value for geokey in self.geokeys.values()}
        return {**tags, **geokeys}

    def get_tile_idx(self, x: NonNegativeInt, y: NonNegativeInt) -> NonNegativeInt:
        return (y * self.x_tile_count) + x

    @property
    def x_tile_count(self) -> NonNegativeInt:
        if not self.get("ImageWidth") or not self.get("TileWidth"):
            return 0

        return ceil(self["ImageWidth"] / self["TileWidth"])

    @property
    def y_tile_count(self) -> NonNegativeInt:
        if not self.get("ImageHeight") or not self.get("TileHeight"):
            return 0

        return ceil(self["ImageHeight"] / self["TileHeight"])

    def has_tile(self, x: NonNegativeInt, y: NonNegativeInt) -> bool:
        idx = self.get_tile_idx(x, y)
        tile_offsets = self.get("TileOffsets", [])
        tile_byte_counts = self.get("TileByteCounts", [])

        tile_exist = self.x_tile_count > 0 and self.y_tile_count > 0
        tile_data_exist = len(tile_offsets) > idx and len(tile_byte_counts) > idx

        return tile_exist and tile_data_exist

    @property
    def numpy_shape(self) -> tuple:
        n_bands = self.get("SamplesPerPixel")
        width = self.get("TileWidth")
        height = self.get("TileHeight")

        return width, height, n_bands

    @property
    def numpy_dtype(self) -> np.dtype:
        sample_format = self["SampleFormat"][0]
        bits_per_sample = self["BitsPerSample"][0]

        FORMAT_MAPPING = {1: "uint", 2: "int", 3: "float"}

        type_str = FORMAT_MAPPING.get(sample_format, "uint")

        return np.dtype(f"{type_str}{bits_per_sample}")

    def parse_geokeys(self) -> None:
        """
        Parse values stored in GeoDoubleParamsTag and GeoAsciiParamsTag and enrich
        GeoKeyDirectoryTag with them

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
        if "GeoKeyDirectoryTag" not in self:
            return

        dir_tag = self["GeoKeyDirectoryTag"]

        version, _, _, keys_n = dir_tag[:4]
        assert version == 1

        for i in range(1, keys_n + 1):
            geokey_code, tag_code, length, value = dir_tag[4 * i : 4 * (i + 1)]
            offset = None

            if tag_code != 0:
                offset = value
                value = None

            if tag_code > 0:
                tag_name = TagCode(tag_code).name
                tag_value = self[tag_name]

                if tag_name == "GeoAsciiParamsTag":
                    start = offset
                    end = offset + length
                    # We omit "|" symbol, which separates ASCII values in the string
                    # by reducing line length by 1
                    value = tag_value[start : end - 1]

                else:
                    value = tag_value[offset]

            geo_key = GeoKey(code=geokey_code, value=value)

            self[geo_key.name] = geo_key
