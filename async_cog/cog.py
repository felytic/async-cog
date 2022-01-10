from __future__ import annotations

from struct import calcsize, pack, unpack
from typing import Any, Iterator, List, Literal

from aiohttp import ClientSession

from async_cog.ifd import IFD, Tag


class COGReader:
    _version: int
    _first_ifd_pointer: int
    _ifds: List[IFD]
    # For characters meainng in *_fmt
    # https://docs.python.org/3.10/library/struct.html#format-characters
    _endian_fmt: Literal["<", ">"]
    _pointer_fmt: Literal["I", "Q"]
    _n_fmt: Literal["H", "Q"]

    def __init__(self, url: str):
        self._url: str = url
        self._ifds = []

    async def __aenter__(self) -> COGReader:
        self._client = ClientSession()
        try:
            await self._read_header()
            await self._read_idfs()
        except AssertionError:
            raise ValueError("Invalid file format")

        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self._client.close()

    async def _read(self, offset: int, size: int) -> bytes:
        header = {"Range": f"bytes={offset}-{offset + size - 1}"}

        async with self._client.get(self.url, headers=header) as response:
            assert response.ok
            return await response.read()

    @property
    def tag_format(self) -> str:
        return self.format(f"HH2{self._pointer_fmt}")

    @property
    def url(self) -> str:
        return self._url

    @property
    def is_bigtiff(self) -> bool:
        return self._version == 43

    def format(self, format_str: str) -> str:
        return f"{self._endian_fmt}{format_str}"

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
        OFFSET = 0

        data = await self._read(OFFSET, 4)

        (endian,) = unpack("2s2x", data)

        if endian == b"II":
            self._endian_fmt = "<"
        elif endian == b"MM":
            self._endian_fmt = ">"
        else:
            raise AssertionError

        (version,) = unpack(self.format("2xH"), data)

        assert version == 42 or version == 43
        self._version = version

    async def _read_tiff_second_header(self) -> int:
        """
        Second header structure for TIFF

        +------+-----+---------------------+
        |offset| size|                value|
        +------+-----+---------------------+
        |     4|    4| Pointer to first IFD|
        +------+-----+---------------------+
        """
        OFFSET = 4

        data = await self._read(OFFSET, calcsize(self._pointer_fmt))
        (first_ifd_pointer,) = unpack(self.format(self._pointer_fmt), data)

        return int(first_ifd_pointer)

    async def _read_bigtiff_second_header(self) -> int:
        """
        Second header structure for BigTIFF

        +------+-----+----------------------------------------------+
        |offset| size|                                         value|
        +------+-----+----------------------------------------------+
        |     4|    2| Bytesize of IFD pointers (should always be 8)|
        +------+-----+----------------------------------------------+
        |     6|    2|                                      Always 0|
        +------+-----+----------------------------------------------+
        |     8|    8|                          Pointer to first IFD|
        +------+-----+----------------------------------------------+
        """

        OFFSET = 4
        format_str = self.format("HHQ")

        data = await self._read(OFFSET, calcsize(format_str))

        bytesize, placeholder, pointer = unpack(format_str, data)

        assert bytesize == 8
        assert placeholder == 0

        return int(pointer)

    async def _read_header(self) -> None:
        """
        Reads TIFF header. See functions docstrings to get it's structure
        """
        await self._read_first_header()

        if self.is_bigtiff:
            self._pointer_fmt = "Q"
            self._n_fmt = "Q"

            self._first_ifd_pointer = await self._read_bigtiff_second_header()
        else:
            self._pointer_fmt = "I"
            self._n_fmt = "H"

            self._first_ifd_pointer = await self._read_tiff_second_header()

    def tag_from_tag_data(self, tag_data: bytes) -> Tag:
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
        code, tag_type, n_values, pointer = unpack(self.tag_format, tag_data)

        tag = Tag(code=code, type=tag_type, n_values=n_values, pointer=pointer)

        if tag.data_size <= calcsize(self._pointer_fmt):
            tag.data = pack(self._pointer_fmt, pointer)[: tag.data_size]
            tag.pointer = 0

        return tag

    def tags_from_data(self, n_tags: int, tags_data: bytes) -> Iterator[Tag]:
        size = calcsize(self.tag_format)

        for tag_data in unpack(n_tags * f"{size}s", tags_data):
            try:
                tag = self.tag_from_tag_data(tag_data)
            except ValueError:
                continue

            yield tag

    async def _read_ifd(self, ifd_pointer: int) -> IFD:
        """
        IFD structure (all offsets are relative to ifd_offset):
        +------------+------------+------------------------------------------+
        |      offset|        size|                                     value|
        +------------+------------+------------------------------------------+
        |           0|  ifd_n_size|                 n — number of tags in IFD|
        +------------+------------+------------------------------------------+
        |           2|    tag_size|                                Tag 0 data|
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

        n_format = self.format(self._n_fmt)

        n_data = await self._read(ifd_pointer, calcsize(n_format))
        (n_tags,) = unpack(n_format, n_data)

        tags_len = n_tags * calcsize(self.tag_format)
        ifd_offset = ifd_pointer + calcsize(n_format)
        ifd_format = self.format(f"{tags_len}s{self._pointer_fmt}")

        ifd_data = await self._read(ifd_offset, calcsize(ifd_format))

        tags_data, pointer = unpack(ifd_format, ifd_data)
        tags = self.tags_from_data(n_tags, tags_data)

        return IFD(
            offset=ifd_pointer,
            n_tags=n_tags,
            next_ifd_pointer=pointer,
            tags=tags,
        )

    async def _read_idfs(self) -> None:
        pointer = self._first_ifd_pointer

        while pointer > 0:
            ifd = await self._read_ifd(pointer)
            self._ifds.append(ifd)
            pointer = ifd.next_ifd_pointer
