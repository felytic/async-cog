# Thanks to mapbox/COGDumper for the mock data
from pathlib import Path
from typing import Any

import pytest
from aioresponses import CallbackResult, aioresponses

from async_cog import COGReader
from async_cog.ifd import IFD, Tag


def test_constructor() -> None:
    url = "http://example.com"
    reader = COGReader(url)

    assert reader.url == url


def response_read(url: str, **kwargs: Any) -> CallbackResult:
    path = (Path.cwd() / Path(__file__).parent).resolve()
    with open(path / "mock_data" / str(url), "rb") as file:
        range_header = kwargs["headers"]["Range"]
        offset_start, offset_end = map(int, range_header.split("bytes=")[1].split("-"))
        file.seek(offset_start)
        data = file.read(offset_end - offset_start + 1)
        return CallbackResult(body=data, content_type="image/tiff")


@pytest.mark.asyncio
async def test_read_header() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert not reader.is_bigtiff


@pytest.mark.asyncio
async def test_read_bigtiff_header() -> None:
    url = "BigTIFF.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert reader.is_bigtiff


@pytest.mark.asyncio
async def test_read_big_endian_header() -> None:
    url = "be_cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert reader._byte_order_fmt == ">"


@pytest.mark.asyncio
async def test_read_invalid_header() -> None:
    url = "invalid_cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        with pytest.raises(ValueError, match="Invalid file format"):
            await COGReader(url).__aenter__()


@pytest.mark.asyncio
async def test_read_invalid_endian() -> None:
    url = "invalid_endian.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        with pytest.raises(ValueError, match="Invalid file format"):
            await COGReader(url).__aenter__()


@pytest.mark.asyncio
async def test_read_ifds() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert reader._ifds == [
                IFD(
                    pointer=8,
                    n_tags=13,
                    next_ifd_pointer=4282,
                    tags=[
                        Tag(code=256, type=3, n_values=1, data=b"@\x00"),
                        Tag(code=257, type=3, n_values=1, data=b"@\x00"),
                        Tag(code=258, type=3, n_values=3, data_pointer=170, data=None),
                        Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
                        Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                        Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                        Tag(code=322, type=3, n_values=1, data=b"\x00\x01"),
                        Tag(code=323, type=3, n_values=1, data=b"\x00\x01"),
                        Tag(
                            code=324,
                            type=4,
                            n_values=1,
                            data=b"\xff\x00\x00\x00",
                        ),
                        Tag(
                            code=325,
                            type=4,
                            n_values=1,
                            data=b"\xbb\x0f\x00\x00",
                        ),
                        Tag(code=339, type=3, n_values=3, data_pointer=176, data=None),
                        Tag(code=347, type=7, n_values=73, data_pointer=182, data=None),
                    ],
                ),
                IFD(
                    pointer=4282,
                    n_tags=14,
                    next_ifd_pointer=4542,
                    tags=[
                        Tag(
                            code=254,
                            type=4,
                            n_values=1,
                            data=b"\x01\x00\x00\x00",
                        ),
                        Tag(code=256, type=3, n_values=1, data=b" \x00"),
                        Tag(code=257, type=3, n_values=1, data=b" \x00"),
                        Tag(code=258, type=3, n_values=3, data_pointer=4456, data=None),
                        Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
                        Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                        Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                        Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                        Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(
                            code=324,
                            type=4,
                            n_values=1,
                            data=b"\xc9\x14\x00\x00",
                        ),
                        Tag(
                            code=325,
                            type=4,
                            n_values=1,
                            data=b"\xd7\x08\x00\x00",
                        ),
                        Tag(code=339, type=3, n_values=3, data_pointer=4462, data=None),
                        Tag(
                            code=347, type=7, n_values=73, data_pointer=4468, data=None
                        ),
                    ],
                ),
                IFD(
                    pointer=4542,
                    n_tags=14,
                    next_ifd_pointer=4802,
                    tags=[
                        Tag(
                            code=254,
                            type=4,
                            n_values=1,
                            data=b"\x01\x00\x00\x00",
                        ),
                        Tag(code=256, type=3, n_values=1, data=b"\x10\x00"),
                        Tag(code=257, type=3, n_values=1, data=b"\x10\x00"),
                        Tag(code=258, type=3, n_values=3, data_pointer=4716, data=None),
                        Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
                        Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                        Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                        Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                        Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(
                            code=324,
                            type=4,
                            n_values=1,
                            data=b"\xa0\x1d\x00\x00",
                        ),
                        Tag(
                            code=325,
                            type=4,
                            n_values=1,
                            data=b"\xe4\x03\x00\x00",
                        ),
                        Tag(code=339, type=3, n_values=3, data_pointer=4722, data=None),
                        Tag(
                            code=347, type=7, n_values=73, data_pointer=4728, data=None
                        ),
                    ],
                ),
                IFD(
                    pointer=4802,
                    n_tags=14,
                    next_ifd_pointer=5062,
                    tags=[
                        Tag(
                            code=254,
                            type=4,
                            n_values=1,
                            data=b"\x01\x00\x00\x00",
                        ),
                        Tag(code=256, type=3, n_values=1, data=b"\x08\x00"),
                        Tag(code=257, type=3, n_values=1, data=b"\x08\x00"),
                        Tag(code=258, type=3, n_values=3, data_pointer=4976, data=None),
                        Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
                        Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                        Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                        Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                        Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(
                            code=324,
                            type=4,
                            n_values=1,
                            data=b"\x84!\x00\x00",
                        ),
                        Tag(
                            code=325,
                            type=4,
                            n_values=1,
                            data=b"\xa7\x03\x00\x00",
                        ),
                        Tag(code=339, type=3, n_values=3, data_pointer=4982, data=None),
                        Tag(
                            code=347, type=7, n_values=73, data_pointer=4988, data=None
                        ),
                    ],
                ),
                IFD(
                    pointer=5062,
                    n_tags=14,
                    next_ifd_pointer=0,
                    tags=[
                        Tag(
                            code=254,
                            type=4,
                            n_values=1,
                            data=b"\x01\x00\x00\x00",
                        ),
                        Tag(code=256, type=3, n_values=1, data=b"\x04\x00"),
                        Tag(code=257, type=3, n_values=1, data=b"\x04\x00"),
                        Tag(code=258, type=3, n_values=3, data_pointer=5236, data=None),
                        Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
                        Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                        Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                        Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                        Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                        Tag(code=324, type=4, n_values=1, data=b"+%\x00\x00"),
                        Tag(
                            code=325,
                            type=4,
                            n_values=1,
                            data=b"&\x05\x00\x00",
                        ),
                        Tag(code=339, type=3, n_values=3, data_pointer=5242, data=None),
                        Tag(
                            code=347, type=7, n_values=73, data_pointer=5248, data=None
                        ),
                    ],
                ),
            ]


@pytest.mark.asyncio
async def test_read_ifds_big_tiff() -> None:
    url = "BigTIFF.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            ifds = reader._ifds

    assert ifds == [
        IFD(
            pointer=16,
            n_tags=12,
            next_ifd_pointer=196880,
            tags=[
                Tag(code=256, type=3, n_values=1, data=b"@\x00"),
                Tag(code=257, type=3, n_values=1, data=b"@\x00"),
                Tag(
                    code=258,
                    type=3,
                    n_values=3,
                    data=b"\x08\x00\x08\x00\x08\x00",
                ),
                Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=322, type=3, n_values=1, data=b"\x00\x01"),
                Tag(code=323, type=3, n_values=1, data=b"\x00\x01"),
                Tag(
                    code=324,
                    type=16,
                    n_values=1,
                    data=b"\x10\x01\x00\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=325,
                    type=16,
                    n_values=1,
                    data=b"\x00\x00\x03\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=339,
                    type=3,
                    n_values=3,
                    data=b"\x01\x00\x01\x00\x01\x00",
                ),
            ],
        ),
        IFD(
            pointer=196880,
            n_tags=13,
            next_ifd_pointer=197156,
            tags=[
                Tag(code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"),
                Tag(code=256, type=3, n_values=1, data=b" \x00"),
                Tag(code=257, type=3, n_values=1, data=b" \x00"),
                Tag(
                    code=258,
                    type=3,
                    n_values=3,
                    data=b"\x08\x00\x08\x00\x08\x00",
                ),
                Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                Tag(
                    code=324,
                    type=16,
                    n_values=1,
                    data=b"`\x05\x03\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=325,
                    type=16,
                    n_values=1,
                    data=b"\x00\xc0\x00\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=339,
                    type=3,
                    n_values=3,
                    data=b"\x01\x00\x01\x00\x01\x00",
                ),
            ],
        ),
        IFD(
            pointer=197156,
            n_tags=13,
            next_ifd_pointer=197432,
            tags=[
                Tag(code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"),
                Tag(code=256, type=3, n_values=1, data=b"\x10\x00"),
                Tag(code=257, type=3, n_values=1, data=b"\x10\x00"),
                Tag(
                    code=258,
                    type=3,
                    n_values=3,
                    data=b"\x08\x00\x08\x00\x08\x00",
                ),
                Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                Tag(
                    code=324,
                    type=16,
                    n_values=1,
                    data=b"`\xc5\x03\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=325,
                    type=16,
                    n_values=1,
                    data=b"\x00\xc0\x00\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=339,
                    type=3,
                    n_values=3,
                    data=b"\x01\x00\x01\x00\x01\x00",
                ),
            ],
        ),
        IFD(
            pointer=197432,
            n_tags=13,
            next_ifd_pointer=197708,
            tags=[
                Tag(code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"),
                Tag(code=256, type=3, n_values=1, data=b"\x08\x00"),
                Tag(code=257, type=3, n_values=1, data=b"\x08\x00"),
                Tag(
                    code=258,
                    type=3,
                    n_values=3,
                    data=b"\x08\x00\x08\x00\x08\x00",
                ),
                Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                Tag(
                    code=324,
                    type=16,
                    n_values=1,
                    data=b"`\x85\x04\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=325,
                    type=16,
                    n_values=1,
                    data=b"\x00\xc0\x00\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=339,
                    type=3,
                    n_values=3,
                    data=b"\x01\x00\x01\x00\x01\x00",
                ),
            ],
        ),
        IFD(
            pointer=197708,
            n_tags=13,
            next_ifd_pointer=0,
            tags=[
                Tag(code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"),
                Tag(code=256, type=3, n_values=1, data=b"\x04\x00"),
                Tag(code=257, type=3, n_values=1, data=b"\x04\x00"),
                Tag(
                    code=258,
                    type=3,
                    n_values=3,
                    data=b"\x08\x00\x08\x00\x08\x00",
                ),
                Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=262, type=3, n_values=1, data=b"\x02\x00"),
                Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
                Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
                Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
                Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
                Tag(
                    code=324,
                    type=16,
                    n_values=1,
                    data=b"`E\x05\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=325,
                    type=16,
                    n_values=1,
                    data=b"\x00\xc0\x00\x00\x00\x00\x00\x00",
                ),
                Tag(
                    code=339,
                    type=3,
                    n_values=3,
                    data=b"\x01\x00\x01\x00\x01\x00",
                ),
            ],
        ),
    ]


def test_tag_format() -> None:
    tag = Tag(code=254, type=4, n_values=13)
    assert tag.format == "13I"
    assert tag.data_pointer is None


def test_tag_size() -> None:
    tag = Tag(code=254, type=4, n_values=13)
    assert tag.data_size == 52


def test_tag_name() -> None:
    tag = Tag(code=34735, type=3, n_values=32, data_pointer=502)
    assert tag.name == "GeoKeyDirectoryTag"
