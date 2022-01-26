from __future__ import annotations

from struct import calcsize, pack, unpack
from typing import Any, Iterator, List, Literal

from aiohttp import ClientSession

from async_cog.ifd import IFD
from async_cog.tag import Tag


class COGReader:
    _version: int
    _first_ifd_pointer: int
    _ifds: List[IFD]
    # For characters meainng in *_fmt attributes see:
    # https://docs.python.org/3.10/library/struct.html#format-characters
    _byte_order_fmt: Literal["<", ">"]
    _pointer_fmt: Literal["I", "Q"]
    _n_fmt: Literal["H", "Q"]

    def __init__(self, url: str):
        self._url: str = url
        self._ifds = []

    async def __aenter__(self) -> COGReader:
        """
        Establish client session and read COG's metadata
        """

        self._client = ClientSession()

        try:
            await self._read_header()
            await self._read_idfs()
        except AssertionError:
            raise ValueError("Invalid file format")

        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self._client.close()

    @property
    def url(self) -> str:
        return self._url

    @property
    def is_bigtiff(self) -> bool:
        """
        Is this GOG in the BigTIFF format
        """

        return self._version == 43

    @property
    def _tag_format(self) -> str:
        """
        Return format string for struct.unpack(): two SHORTs and two pointer types.
        For detailed tag structure see _tag_from_tag_bytes()
        """

        return self._format(f"2H2{self._pointer_fmt}")

    def _format(self, format_str: str) -> str:
        """
        Add byte-order endian to struct format string
        """

        return f"{self._byte_order_fmt}{format_str}"

    async def _read(self, offset: int, size: int) -> bytes:
        """
        Get the data from URL within the specific byte range
        """

        header = {"Range": f"bytes={offset}-{offset + size - 1}"}

        async with self._client.get(self.url, headers=header) as response:
            assert response.ok
            return await response.read()

    async def _read_header(self) -> None:
        """
        Reads TIFF header. See functions docstrings to get it's structure
        """

        await self._read_first_header()

        if self.is_bigtiff:
            self._pointer_fmt = "Q"  # 8 byte unsigned int
            self._n_fmt = "Q"  # 8 byte unsigned int

            await self._read_bigtiff_second_header()
        else:
            self._pointer_fmt = "I"  # 4 byte unsigned int
            self._n_fmt = "H"  # 2 byte unsigned int

            await self._read_second_header()

    async def _read_idfs(self) -> None:
        """
        Get data for IFDs (Image File Directories).
        See IFD structure in _read_ifd() docstring
        """

        pointer = self._first_ifd_pointer

        while pointer > 0:
            ifd = await self._read_ifd(pointer)
            self._ifds.append(ifd)
            pointer = ifd.next_ifd_pointer

    async def _read_first_header(self) -> None:
        """
        First header structure

        +------+-----+------------------------------------------------+
        |offset| size|                                           value|
        +------+-----+------------------------------------------------+
        |     0|    2|               "II" for little-endian byte order|
        |      |     |               "MM" for big-endian byte order   |
        +------+-----+------------------------------------------------+
        |     2|    2| Version number (42 for TIFF and 43 for BigTIFF)|
        +------+-----+------------------------------------------------+
        """

        POINTER = 0

        data = await self._read(POINTER, 4)

        # Read first two bytes and skip the last two
        (first_bytest,) = unpack("2s2x", data)

        # https://docs.python.org/3.8/library/struct.html#byte-order-size-and-alignment
        if first_bytest == b"II":
            self._byte_order_fmt = "<"
        elif first_bytest == b"MM":
            self._byte_order_fmt = ">"
        else:
            raise AssertionError

        # Skip first two bytes and read the last two as SHORT
        (self._version,) = unpack(self._format("2xH"), data)

        assert self._version in (42, 43)

    async def _read_second_header(self) -> None:
        """
        Second header structure for TIFF.
        It's pointer is 4 since the first 4 bystes are for the first header

        +------+-----+---------------------+
        |offset| size|                value|
        +------+-----+---------------------+
        |     0|    4| Pointer to first IFD|
        +------+-----+---------------------+
        """

        POINTER = 4
        format_str = self._format(self._pointer_fmt)

        data = await self._read(POINTER, calcsize(format_str))
        (self._first_ifd_pointer,) = unpack(format_str, data)

    async def _read_bigtiff_second_header(self) -> None:
        """
        Second header structure for BigTIFF
        It's pointer is 4 since the first 4 bystes are for the first header

        +------+-----+----------------------------------------------+
        |offset| size|                                         value|
        +------+-----+----------------------------------------------+
        |     0|    2| Bytesize of IFD pointers (should always be 8)|
        +------+-----+----------------------------------------------+
        |     2|    2|                                      Always 0|
        +------+-----+----------------------------------------------+
        |     4|    8|                          Pointer to first IFD|
        +------+-----+----------------------------------------------+
        """

        POINTER = 4
        format_str = self._format("HHQ")

        data = await self._read(POINTER, calcsize(format_str))

        bytesize, placeholder, self._first_ifd_pointer = unpack(format_str, data)

        assert bytesize == 8
        assert placeholder == 0

    async def _read_ifd(self, ifd_pointer: int) -> IFD:
        """
        IFD structure. It's pointer is `ifd_pointer`

        +------------+------------+------------------------------------------+
        |      offset|        size|                                     value|
        +------------+------------+------------------------------------------+
        |           0|  ifd_n_size|                 n — number of tags in IFD|
        +------------+------------+------------------------------------------+
        |  ifd_n_size|    tag_size|                                Tag 0 data|
        +------------+------------+------------------------------------------+
        |         ...|         ...|                                       ...|
        +------------+------------+------------------------------------------+
        |2+x*tag_size|    tag_size|                                     Tag x|
        +------------+------------+------------------------------------------+
        |         ...|         ...|                                       ...|
        +------------+------------+------------------------------------------+
        |2+n*tag_size|pointer_size|                      Pointer to next IFD |
        +------------+------------+------------------------------------------+
        """

        n_format_str = self._format(self._n_fmt)

        # Read nubmer of tags in the IFD
        n_data = await self._read(ifd_pointer, calcsize(n_format_str))
        (n_tags,) = unpack(n_format_str, n_data)

        tags_len = n_tags * calcsize(self._tag_format)
        tags_pointer = ifd_pointer + calcsize(n_format_str)
        format_str = self._format(f"{tags_len}s{self._pointer_fmt}")

        # Read tags data and pointer to next IFD
        data = await self._read(tags_pointer, calcsize(format_str))

        tags_data, next_ifd_pointer = unpack(format_str, data)
        tags = self._tags_from_data(n_tags, tags_data)

        return IFD(
            pointer=ifd_pointer,
            n_tags=n_tags,
            next_ifd_pointer=next_ifd_pointer,
            tags={tag.name: tag for tag in tags},
        )

    def _tags_from_data(self, n_tags: int, tags_bytes: bytes) -> Iterator[Tag]:
        """
        Split data into tag-sized buffers and parse them
        """

        size = calcsize(self._tag_format)

        # Split tags_bytes into n tag-sized chuncks
        for tag_bytes in unpack(n_tags * f"{size}s", tags_bytes):
            try:
                tag = self._tag_from_tag_bytes(tag_bytes)
            except ValueError:
                continue

            yield tag

    def _tag_from_tag_bytes(self, tag_bytes: bytes) -> Tag:
        """
        Tag structure

        +--------------+------------+-----------------------------------+
        |        offset|        size|                              value|
        +--------------+------------+-----------------------------------+
        |             0|           2|       Tag code (see ifd.TAG_NAMES)|
        +--------------+------------+-----------------------------------+
        |             2|           2|  Tag data type (see ifd.TAG_TYPES)|
        +--------------+------------+-----------------------------------+
        |             4|pointer_size|                   Number of values|
        +--------------+------------+-----------------------------------+
        |4+pointer_size|pointer_size| Pointer to the data or data itself|
        |              |            |       if it's size <= pointer_size|
        +--------------+------------+-----------------------------------+
        """

        code, tag_type, n_values, pointer = unpack(self._tag_format, tag_bytes)

        tag = Tag(code=code, type=tag_type, n_values=n_values, data_pointer=pointer)

        # If tag data type fits into it's data pointer size, then last bytes contain
        # data, not it's pointer
        if tag.data_size <= calcsize(self._pointer_fmt):
            tag.data = pack(self._pointer_fmt, pointer)[: tag.data_size]
            tag.data_pointer = None

        return tag

    async def _fill_tag_with_data(self, tag: Tag) -> None:
        """
        Read tag-related data from specific place in the file.
        And parse values from it according to tag's format
        """

        if tag.data_pointer:
            tag.data = await self._read(tag.data_pointer, tag.data_size)

        tag.parse_data(self._byte_order_fmt)

    async def _fill_ifd_with_data(self, ifd: IFD) -> None:
        """
        Read data for all tags within IFD. Parse GeoKeys tags
        """

        for tag in ifd.tags.values():
            await self._fill_tag_with_data(tag)

        ifd.parse_geokeys()
