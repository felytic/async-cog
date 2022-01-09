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
            assert reader._byte_order == "big"


@pytest.mark.asyncio
async def test_read_invalid_header() -> None:
    url = "invalid_cog.tif"

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
                    offset=8,
                    n_tags=13,
                    next_ifd_pointer=4282,
                    tags=[
                        Tag(code=256, type=3, n_values=1, pointer=4194304),
                        Tag(code=257, type=3, n_values=1, pointer=4194304),
                        Tag(code=258, type=3, n_values=3, pointer=11141120),
                        Tag(code=259, type=3, n_values=1, pointer=458752),
                        Tag(code=277, type=3, n_values=1, pointer=196608),
                        Tag(code=284, type=3, n_values=1, pointer=65536),
                        Tag(code=322, type=3, n_values=1, pointer=16777216),
                        Tag(code=323, type=3, n_values=1, pointer=16777216),
                        Tag(code=324, type=4, n_values=1, pointer=16711680),
                        Tag(code=325, type=4, n_values=1, pointer=263913472),
                        Tag(code=339, type=3, n_values=3, pointer=11534336),
                        Tag(code=347, type=7, n_values=73, pointer=11927552),
                    ],
                ),
                IFD(
                    offset=4282,
                    n_tags=14,
                    next_ifd_pointer=4542,
                    tags=[
                        Tag(code=254, type=4, n_values=1, pointer=65536),
                        Tag(code=256, type=3, n_values=1, pointer=2097152),
                        Tag(code=257, type=3, n_values=1, pointer=2097152),
                        Tag(code=258, type=3, n_values=3, pointer=292028416),
                        Tag(code=259, type=3, n_values=1, pointer=458752),
                        Tag(code=262, type=3, n_values=1, pointer=131072),
                        Tag(code=277, type=3, n_values=1, pointer=196608),
                        Tag(code=284, type=3, n_values=1, pointer=65536),
                        Tag(code=322, type=3, n_values=1, pointer=8388608),
                        Tag(code=323, type=3, n_values=1, pointer=8388608),
                        Tag(code=324, type=4, n_values=1, pointer=348717056),
                        Tag(code=325, type=4, n_values=1, pointer=148307968),
                        Tag(code=339, type=3, n_values=3, pointer=292421632),
                        Tag(code=347, type=7, n_values=73, pointer=292814848),
                    ],
                ),
                IFD(
                    offset=4542,
                    n_tags=14,
                    next_ifd_pointer=4802,
                    tags=[
                        Tag(code=254, type=4, n_values=1, pointer=65536),
                        Tag(code=256, type=3, n_values=1, pointer=1048576),
                        Tag(code=257, type=3, n_values=1, pointer=1048576),
                        Tag(code=258, type=3, n_values=3, pointer=309067776),
                        Tag(code=259, type=3, n_values=1, pointer=458752),
                        Tag(code=262, type=3, n_values=1, pointer=131072),
                        Tag(code=277, type=3, n_values=1, pointer=196608),
                        Tag(code=284, type=3, n_values=1, pointer=65536),
                        Tag(code=322, type=3, n_values=1, pointer=8388608),
                        Tag(code=323, type=3, n_values=1, pointer=8388608),
                        Tag(code=324, type=4, n_values=1, pointer=497025024),
                        Tag(code=325, type=4, n_values=1, pointer=65273856),
                        Tag(code=339, type=3, n_values=3, pointer=309460992),
                        Tag(code=347, type=7, n_values=73, pointer=309854208),
                    ],
                ),
                IFD(
                    offset=4802,
                    n_tags=14,
                    next_ifd_pointer=5062,
                    tags=[
                        Tag(code=254, type=4, n_values=1, pointer=65536),
                        Tag(code=256, type=3, n_values=1, pointer=524288),
                        Tag(code=257, type=3, n_values=1, pointer=524288),
                        Tag(code=258, type=3, n_values=3, pointer=326107136),
                        Tag(code=259, type=3, n_values=1, pointer=458752),
                        Tag(code=262, type=3, n_values=1, pointer=131072),
                        Tag(code=277, type=3, n_values=1, pointer=196608),
                        Tag(code=284, type=3, n_values=1, pointer=65536),
                        Tag(code=322, type=3, n_values=1, pointer=8388608),
                        Tag(code=323, type=3, n_values=1, pointer=8388608),
                        Tag(code=324, type=4, n_values=1, pointer=562298880),
                        Tag(code=325, type=4, n_values=1, pointer=61276160),
                        Tag(code=339, type=3, n_values=3, pointer=326500352),
                        Tag(code=347, type=7, n_values=73, pointer=326893568),
                    ],
                ),
                IFD(
                    offset=5062,
                    n_tags=14,
                    next_ifd_pointer=0,
                    tags=[
                        Tag(code=254, type=4, n_values=1, pointer=65536),
                        Tag(code=256, type=3, n_values=1, pointer=262144),
                        Tag(code=257, type=3, n_values=1, pointer=262144),
                        Tag(code=258, type=3, n_values=3, pointer=343146496),
                        Tag(code=259, type=3, n_values=1, pointer=458752),
                        Tag(code=262, type=3, n_values=1, pointer=131072),
                        Tag(code=277, type=3, n_values=1, pointer=196608),
                        Tag(code=284, type=3, n_values=1, pointer=65536),
                        Tag(code=322, type=3, n_values=1, pointer=8388608),
                        Tag(code=323, type=3, n_values=1, pointer=8388608),
                        Tag(code=324, type=4, n_values=1, pointer=623575040),
                        Tag(code=325, type=4, n_values=1, pointer=86376448),
                        Tag(code=339, type=3, n_values=3, pointer=343539712),
                        Tag(code=347, type=7, n_values=73, pointer=343932928),
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
            offset=16,
            n_tags=12,
            next_ifd_pointer=196880,
            tags=[
                Tag(code=256, type=3, n_values=1, pointer=18014398509481984),
                Tag(code=257, type=3, n_values=1, pointer=18014398509481984),
                Tag(code=258, type=3, n_values=3, pointer=2251799813685248),
                Tag(code=259, type=3, n_values=1, pointer=281474976710656),
                Tag(code=262, type=3, n_values=1, pointer=562949953421312),
                Tag(code=277, type=3, n_values=1, pointer=844424930131968),
                Tag(code=284, type=3, n_values=1, pointer=281474976710656),
                Tag(code=322, type=3, n_values=1, pointer=72057594037927936),
                Tag(code=323, type=3, n_values=1, pointer=72057594037927936),
                Tag(code=324, type=16, n_values=1, pointer=76561193665298432),
                Tag(code=325, type=16, n_values=1, pointer=0),
                Tag(code=339, type=3, n_values=3, pointer=281474976710656),
            ],
        ),
        IFD(
            offset=196880,
            n_tags=13,
            next_ifd_pointer=197156,
            tags=[
                Tag(code=254, type=4, n_values=1, pointer=281474976710656),
                Tag(code=256, type=3, n_values=1, pointer=9007199254740992),
                Tag(code=257, type=3, n_values=1, pointer=9007199254740992),
                Tag(code=258, type=3, n_values=3, pointer=2251799813685248),
                Tag(code=259, type=3, n_values=1, pointer=281474976710656),
                Tag(code=262, type=3, n_values=1, pointer=562949953421312),
                Tag(code=277, type=3, n_values=1, pointer=844424930131968),
                Tag(code=284, type=3, n_values=1, pointer=281474976710656),
                Tag(code=322, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=323, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=324, type=16, n_values=1, pointer=387309567953862656),
                Tag(code=325, type=16, n_values=1, pointer=13835058055282163712),
                Tag(code=339, type=3, n_values=3, pointer=281474976710656),
            ],
        ),
        IFD(
            offset=197156,
            n_tags=13,
            next_ifd_pointer=197432,
            tags=[
                Tag(code=254, type=4, n_values=1, pointer=281474976710656),
                Tag(code=256, type=3, n_values=1, pointer=4503599627370496),
                Tag(code=257, type=3, n_values=1, pointer=4503599627370496),
                Tag(code=258, type=3, n_values=3, pointer=2251799813685248),
                Tag(code=259, type=3, n_values=1, pointer=281474976710656),
                Tag(code=262, type=3, n_values=1, pointer=562949953421312),
                Tag(code=277, type=3, n_values=1, pointer=844424930131968),
                Tag(code=284, type=3, n_values=1, pointer=281474976710656),
                Tag(code=322, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=323, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=324, type=16, n_values=1, pointer=14222367623236026368),
                Tag(code=325, type=16, n_values=1, pointer=13835058055282163712),
                Tag(code=339, type=3, n_values=3, pointer=281474976710656),
            ],
        ),
        IFD(
            offset=197432,
            n_tags=13,
            next_ifd_pointer=197708,
            tags=[
                Tag(code=254, type=4, n_values=1, pointer=281474976710656),
                Tag(code=256, type=3, n_values=1, pointer=2251799813685248),
                Tag(code=257, type=3, n_values=1, pointer=2251799813685248),
                Tag(code=258, type=3, n_values=3, pointer=2251799813685248),
                Tag(code=259, type=3, n_values=1, pointer=281474976710656),
                Tag(code=262, type=3, n_values=1, pointer=562949953421312),
                Tag(code=277, type=3, n_values=1, pointer=844424930131968),
                Tag(code=284, type=3, n_values=1, pointer=281474976710656),
                Tag(code=322, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=323, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=324, type=16, n_values=1, pointer=9610681604808638464),
                Tag(code=325, type=16, n_values=1, pointer=13835058055282163712),
                Tag(code=339, type=3, n_values=3, pointer=281474976710656),
            ],
        ),
        IFD(
            offset=197708,
            n_tags=13,
            next_ifd_pointer=0,
            tags=[
                Tag(code=254, type=4, n_values=1, pointer=281474976710656),
                Tag(code=256, type=3, n_values=1, pointer=1125899906842624),
                Tag(code=257, type=3, n_values=1, pointer=1125899906842624),
                Tag(code=258, type=3, n_values=3, pointer=2251799813685248),
                Tag(code=259, type=3, n_values=1, pointer=281474976710656),
                Tag(code=262, type=3, n_values=1, pointer=562949953421312),
                Tag(code=277, type=3, n_values=1, pointer=844424930131968),
                Tag(code=284, type=3, n_values=1, pointer=281474976710656),
                Tag(code=322, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=323, type=3, n_values=1, pointer=36028797018963968),
                Tag(code=324, type=16, n_values=1, pointer=4998995586381250560),
                Tag(code=325, type=16, n_values=1, pointer=13835058055282163712),
                Tag(code=339, type=3, n_values=3, pointer=281474976710656),
            ],
        ),
    ]


def test_tag_format() -> None:
    tag = Tag(code=254, type=4, n_values=13, pointer=281474976710656)
    assert tag.format == "13L"
