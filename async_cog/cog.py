from typing import Literal

from aiohttp import ClientSession


class COGReader:
    def __init__(self, url: str):
        self._url: str = url
        self._version: Literal[42, 43]
        self._byte_order: Literal["little", "big"]
        self._offset_size: Literal[4, 8]

    async def __aenter__(self):
        self._client = ClientSession()
        try:
            await self._read_header()
        except AssertionError:
            raise ValueError("Invalid file format")

        return self

    async def __aexit__(self, *args, **kwargs):
        await self._client.close()

    async def _read(self, offset: int, bytes: int):
        header = {"Range": f"bytes={offset}-{offset + bytes - 1}"}

        async with self._client.get(self.url, headers=header) as response:
            assert response.ok
            return await response.read()

    async def _read_first_header(self):
        """
        First header structure

        +------+-----+------------------------------------------------+
        |offset|bytes|                                           value|
        +------+-----+------------------------------------------------+
        |     0|    2|               "II" for little-endian byte order|
        |      |     |               "MM" for big-endian byte order   |
        +------+-----+------------------------------------------------+
        |     2|    2| Version number (42 for TIFF and 43 for BigTIFF)|
        +------+-----+------------------------------------------------+
        """

        ENDIAN_OFFSET = 0
        ENDIAN_BYTES = 2

        VERSION_OFFSET = 2
        VERSION_BYTES = 2

        bytes = await self._read(ENDIAN_OFFSET, ENDIAN_BYTES + VERSION_BYTES)

        endian = bytes[ENDIAN_OFFSET:ENDIAN_BYTES]
        version_bytes = bytes[VERSION_OFFSET:]

        assert endian in (b"II", b"MM")

        if endian == b"II":
            self._byte_order = "little"
        elif endian == b"MM":
            self._byte_order = "big"

        version = int.from_bytes(version_bytes, self._byte_order)

        assert version == 42 or version == 43
        self._version = version

    async def _read_tiff_second_header(self) -> int:
        """
        Second header structure for TIFF

        +------+-----+---------------------+
        |offset|bytes|                value|
        +------+-----+---------------------+
        |     4|    4| Pointer to first IFD|
        +------+-----+---------------------+
        """
        self._offset_size = 4
        POINTER_OFFSET = 4

        bytes = await self._read(POINTER_OFFSET, self._offset_size)
        first_ifd_pointer = int.from_bytes(bytes, self._byte_order)

        return first_ifd_pointer

    async def _read_bigtiff_second_header(self) -> int:
        """
        Second header structure for BigTIFF

        +------+-----+----------------------------------------------+
        |offset|bytes|                                         value|
        +------+-----+----------------------------------------------+
        |     4|    2| Bytesize of IFD pointers (should always be 8)|
        +------+-----+----------------------------------------------+
        |     6|    2|                                      Always 0|
        +------+-----+----------------------------------------------+
        |     8|    8|                          Pointer to first IFD|
        +------+-----+----------------------------------------------+
        """

        self._offset_size = 8

        BYTESIZE_OFFSET = 4
        BYTESIZE_BYTES = 2
        PLACEHOLDER_BYTES = 2

        bytes = await self._read(
            BYTESIZE_OFFSET,
            BYTESIZE_BYTES + PLACEHOLDER_BYTES + self._offset_size,
        )

        bytesize_data = bytes[:BYTESIZE_BYTES]
        bytesize = int.from_bytes(bytesize_data, self._byte_order)

        assert bytesize == 8

        placeholder_data = bytes[BYTESIZE_BYTES:PLACEHOLDER_BYTES]
        placeholder = int.from_bytes(placeholder_data, self._byte_order)

        assert placeholder == 0

        pointer_data = bytes[-self._offset_size :]
        first_ifd_pointer = int.from_bytes(pointer_data, self._byte_order)

        return first_ifd_pointer

    async def _read_header(self):
        """
        Reads TIFF header. See functions docstrings to get it's structure
        """
        await self._read_first_header()

        if self.is_bigtiff:
            await self._read_bigtiff_second_header()
        else:
            await self._read_tiff_second_header()

    @property
    def url(self):
        return self._url

    @property
    def is_bigtiff(self):
        return self._version == 43
