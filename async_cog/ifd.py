from typing import Any, Dict, Union

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
