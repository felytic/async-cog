from typing import Any, Dict

from pydantic import BaseModel

from async_cog.tags import Tag


class IFD(BaseModel):
    pointer: int
    n_tags: int
    next_ifd_pointer: int
    tags: Dict[str, Tag]

    def __getitem__(self, key: str) -> Any:
        return self.tags[key].value

    def __setitem__(self, key: str, tag: Tag) -> None:
        assert tag.name == key
        self.tags[key] = tag

    def __contains__(self, key: str) -> bool:
        return key in self.tags

    def to_dict(self) -> Dict[str, Any]:
        return {
            tag.name: tag.value
            for tag in self.tags.values()
            if not isinstance(tag.value, bytes)
        }

    def parse_geokeys(self) -> None:
        """
        Parse values stored in GeoDoubleParamsTag and GeoAsciiParamsTag and enrich
        GeoKeyDirectoryTag with them
        """

        tag = self.tags.get("GeoKeyDirectoryTag")

        if not tag or not tag.values:
            return

        for geo_key in tag.values:
            if geo_key.tag_code > 0:
                tag_name = geo_key.tag_code.name
                tag_value = self[tag_name]

                if tag_name == "GeoAsciiParamsTag":
                    start = geo_key.offset
                    end = geo_key.offset + geo_key.length
                    # We omit "|" symbol, which separates ASCII values in the string
                    # by reducing line length by 1
                    geo_key.value = tag_value[start : end - 1]

                else:
                    geo_key.value = tag_value[geo_key.offset]
