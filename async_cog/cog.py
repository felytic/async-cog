from __future__ import annotations

from typing import Any, List, Literal

from aiohttp import ClientSession

from async_cog.ifd import IFD, Tag


class COGReader:
    def __init__(self, url: str):
        self._url: str = url
        self._version: int
        self._byte_order: Literal["little", "big"]
        self._pointer_size: Literal[4, 8]
        self._ifd_n_size: Literal[2, 8]
        self._tag_size: Literal[12, 20]
        self._first_ifd_pointer: int
        self._ifds: List[IFD] = []

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

        ENDIAN_OFFSET = 0
        ENDIAN_SIZE = 2

        VERSION_OFFSET = 2
        VERSION_SIZE = 2

        header_data = await self._read(ENDIAN_OFFSET, ENDIAN_SIZE + VERSION_SIZE)

        endian = header_data[ENDIAN_OFFSET:ENDIAN_SIZE]
        version_data = header_data[VERSION_OFFSET:]

        assert endian in (b"II", b"MM")

        if endian == b"II":
            self._byte_order = "little"
        elif endian == b"MM":
            self._byte_order = "big"

        version = int.from_bytes(version_data, self._byte_order)

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
        self._pointer_size = 4
        self._ifd_n_size = 2
        self._tag_size = 12

        POINTER_OFFSET = 4

        pointer_data = await self._read(POINTER_OFFSET, self._pointer_size)
        first_ifd_pointer = int.from_bytes(pointer_data, self._byte_order)

        return first_ifd_pointer

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

        self._pointer_size = 8
        self._ifd_n_size = 8
        self._tag_size = 20

        BYTESIZE_OFFSET = 4
        BYTESIZE_SIZE = 2
        PLACEHOLDER_SIZE = 2

        header_data = await self._read(
            BYTESIZE_OFFSET,
            BYTESIZE_SIZE + PLACEHOLDER_SIZE + self._pointer_size,
        )

        bytesize_data = header_data[:BYTESIZE_SIZE]
        bytesize = int.from_bytes(bytesize_data, self._byte_order)

        assert bytesize == 8

        placeholder_data = header_data[BYTESIZE_SIZE:PLACEHOLDER_SIZE]
        placeholder = int.from_bytes(placeholder_data, self._byte_order)

        assert placeholder == 0

        pointer_data = header_data[-self._pointer_size :]
        first_ifd_pointer = int.from_bytes(pointer_data, self._byte_order)

        return first_ifd_pointer

    async def _read_header(self) -> None:
        """
        Reads TIFF header. See functions docstrings to get it's structure
        """
        await self._read_first_header()

        if self.is_bigtiff:
            self._first_ifd_pointer = await self._read_bigtiff_second_header()
        else:
            self._first_ifd_pointer = await self._read_tiff_second_header()

    def tag_from_tag_data(self, tag_data: bytes) -> Tag:
        CODE_SIZE = 2
        TYPE_SIZE = 2
        N_VALUES_OFFSET = CODE_SIZE + TYPE_SIZE
        N_VALUES_SIZE = 2
        POINTER_OFFSET = N_VALUES_OFFSET + N_VALUES_SIZE

        code_data = tag_data[:CODE_SIZE]
        code = int.from_bytes(code_data, self._byte_order)

        type_data = tag_data[CODE_SIZE : CODE_SIZE + TYPE_SIZE]
        tag_type = int.from_bytes(type_data, self._byte_order)

        n_values_data = tag_data[N_VALUES_OFFSET : N_VALUES_OFFSET + N_VALUES_SIZE]
        n_values = int.from_bytes(n_values_data, self._byte_order)

        pointer_data = tag_data[POINTER_OFFSET : POINTER_OFFSET + self._pointer_size]
        pointer = int.from_bytes(pointer_data, self._byte_order)

        return Tag(code=code, type=tag_type, n_values=n_values, pointer=pointer)

    def tags_from_tags_data(self, n_tags: int, tags_data: bytes) -> List[Tag]:
        tags = []
        for i in range(n_tags):
            data = tags_data[i * self._tag_size : (i + 1) * self._tag_size]
            tag = self.tag_from_tag_data(data)
            tags.append(tag)

        return tags

    async def _read_ifd(self, ifd_pointer: int) -> IFD:
        """
        IFD structure (all offsets are relative to ifd_offset):
        +------+-----+------------------------------------------+
        |offset| size|                                     value|
        +------+-----+------------------------------------------+
        |     0|    2|                 n — number of tags in IFD|
        +------+-----+------------------------------------------+
        |     2|   12|                                Tag 0 data|
        +------+-----+------------------------------------------+
        |   ...|  ...|                                       ...|
        +------+-----+------------------------------------------+
        |2+x*12|   12|                                     Tag x|
        +------+-----+------------------------------------------+
        |   ...|  ...|                                       ...|
        +------+-----+------------------------------------------+
        |2+n*12|   4 | Pointer to next IFD (8 bytes for BigTIFF)|
        +------+-----+------------------------------------------+
        """

        n_data = await self._read(ifd_pointer, self._ifd_n_size)
        n_tags = int.from_bytes(n_data, self._byte_order)

        tags_size = n_tags * self._tag_size + self._pointer_size
        tags_data = await self._read(ifd_pointer + self._ifd_n_size, tags_size)
        tags = self.tags_from_tags_data(n_tags, tags_data)

        next_ifd_pointer_data = tags_data[-self._pointer_size :]
        next_ifd_pointer = int.from_bytes(next_ifd_pointer_data, self._byte_order)

        return IFD(
            offset=ifd_pointer,
            n_tags=n_tags,
            next_ifd_pointer=next_ifd_pointer,
            tags=tags,
        )

    async def _read_idfs(self) -> None:
        pointer = self._first_ifd_pointer

        while pointer > 0:
            ifd = await self._read_ifd(pointer)
            self._ifds.append(ifd)
            pointer = ifd.next_ifd_pointer

    @property
    def url(self) -> str:
        return self._url

    @property
    def is_bigtiff(self) -> bool:
        return self._version == 43
