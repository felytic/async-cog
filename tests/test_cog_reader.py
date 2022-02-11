# Thanks to mapbox/COGDumper for the mock data
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from aioresponses import CallbackResult, aioresponses

from async_cog import COGReader
from async_cog.ifd import IFD
from async_cog.tags import BytesTag, ListTag, NumberTag, StringTag


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
    tags = [
        {
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=64),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=64),
            "BitsPerSample": ListTag(code=258, type=3, length=3, data_pointer=170),
            "Compression": NumberTag(code=259, type=3, length=1, value=7),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=256),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=256),
            "TileOffsets": NumberTag(code=324, type=4, length=1, value=255),
            "TileByteCounts": NumberTag(code=325, type=4, length=1, value=4027),
            "SampleFormat": ListTag(code=339, type=3, length=3, data_pointer=176),
            "JPEGTables": BytesTag(code=347, type=7, length=73, data_pointer=182),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=32),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=32),
            "BitsPerSample": ListTag(code=258, type=3, length=3, data_pointer=4456),
            "Compression": NumberTag(code=259, type=3, length=1, value=7),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=4, length=1, value=5321),
            "TileByteCounts": NumberTag(code=325, type=4, length=1, value=2263),
            "SampleFormat": ListTag(code=339, type=3, length=3, data_pointer=4462),
            "JPEGTables": BytesTag(code=347, type=7, length=73, data_pointer=4468),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=16),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=16),
            "BitsPerSample": ListTag(code=258, type=3, length=3, data_pointer=4716),
            "Compression": NumberTag(code=259, type=3, length=1, value=7),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=4, length=1, value=7584),
            "TileByteCounts": NumberTag(code=325, type=4, length=1, value=996),
            "SampleFormat": ListTag(code=339, type=3, length=3, data_pointer=4722),
            "JPEGTables": BytesTag(code=347, type=7, length=73, data_pointer=4728),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=8),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=8),
            "BitsPerSample": ListTag(code=258, type=3, length=3, data_pointer=4976),
            "Compression": NumberTag(code=259, type=3, length=1, value=7),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=4, length=1, value=8580),
            "TileByteCounts": NumberTag(code=325, type=4, length=1, value=935),
            "SampleFormat": ListTag(code=339, type=3, length=3, data_pointer=4982),
            "JPEGTables": BytesTag(code=347, type=7, length=73, data_pointer=4988),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=4),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=4),
            "BitsPerSample": ListTag(code=258, type=3, length=3, data_pointer=5236),
            "Compression": NumberTag(code=259, type=3, length=1, value=7),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=4, length=1, value=9515),
            "TileByteCounts": NumberTag(code=325, type=4, length=1, value=1318),
            "SampleFormat": ListTag(code=339, type=3, length=3, data_pointer=5242),
            "JPEGTables": BytesTag(code=347, type=7, length=73, data_pointer=5248),
        },
        {
            "GeoKeyDirectoryTag": ListTag(
                code=34735, type=3, length=32, data_pointer=10875
            ),
            "GeoAsciiParamsTag": StringTag(
                code=34737, type=2, length=33, data_pointer=10939
            ),
            "GeoDoubleParamsTag": ListTag(
                code=34736, type=12, length=1, data_pointer=10972
            ),
        },
    ]

    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert reader._ifds == [
                IFD(pointer=8, n_tags=13, next_ifd_pointer=4282, tags=tags[0]),
                IFD(pointer=4282, n_tags=14, next_ifd_pointer=4542, tags=tags[1]),
                IFD(pointer=4542, n_tags=14, next_ifd_pointer=4802, tags=tags[2]),
                IFD(pointer=4802, n_tags=14, next_ifd_pointer=5062, tags=tags[3]),
                IFD(pointer=5062, n_tags=14, next_ifd_pointer=10833, tags=tags[4]),
                IFD(pointer=10833, n_tags=3, next_ifd_pointer=0, tags=tags[5]),
            ]


@pytest.mark.asyncio
async def test_read_ifds_big_tiff() -> None:
    url = "BigTIFF.tif"

    tags = [
        {
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=64),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=64),
            "BitsPerSample": ListTag(code=258, type=3, length=3, value=[8, 8, 8]),
            "Compression": NumberTag(code=259, type=3, length=1, value=1),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=256),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=256),
            "TileOffsets": NumberTag(code=324, type=16, length=1, value=272),
            "TileByteCounts": NumberTag(code=325, type=16, length=1, value=196608),
            "SampleFormat": ListTag(code=339, type=3, length=3, value=[1, 1, 1]),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=32),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=32),
            "BitsPerSample": ListTag(code=258, type=3, length=3, value=[8, 8, 8]),
            "Compression": NumberTag(code=259, type=3, length=1, value=1),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=16, length=1, value=197984),
            "TileByteCounts": NumberTag(code=325, type=16, length=1, value=49152),
            "SampleFormat": ListTag(code=339, type=3, length=3, value=[1, 1, 1]),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=16),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=16),
            "BitsPerSample": ListTag(code=258, type=3, length=3, value=[8, 8, 8]),
            "Compression": NumberTag(code=259, type=3, length=1, value=1),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=16, length=1, value=247136),
            "TileByteCounts": NumberTag(code=325, type=16, length=1, value=49152),
            "SampleFormat": ListTag(code=339, type=3, length=3, value=[1, 1, 1]),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=8),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=8),
            "BitsPerSample": ListTag(code=258, type=3, length=3, value=[8, 8, 8]),
            "Compression": NumberTag(code=259, type=3, length=1, value=1),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=16, length=1, value=296288),
            "TileByteCounts": NumberTag(code=325, type=16, length=1, value=49152),
            "SampleFormat": ListTag(code=339, type=3, length=3, value=[1, 1, 1]),
        },
        {
            "NewSubfileType": NumberTag(code=254, type=4, length=1, value=1),
            "ImageWidth": NumberTag(code=256, type=3, length=1, value=4),
            "ImageHeight": NumberTag(code=257, type=3, length=1, value=4),
            "BitsPerSample": ListTag(code=258, type=3, length=3, value=[8, 8, 8]),
            "Compression": NumberTag(code=259, type=3, length=1, value=1),
            "PhotometricInterpretation": NumberTag(code=262, type=3, length=1, value=2),
            "SamplesPerPixel": NumberTag(code=277, type=3, length=1, value=3),
            "PlanarConfiguration": NumberTag(code=284, type=3, length=1, value=1),
            "TileWidth": NumberTag(code=322, type=3, length=1, value=128),
            "TileHeight": NumberTag(code=323, type=3, length=1, value=128),
            "TileOffsets": NumberTag(code=324, type=16, length=1, value=345440),
            "TileByteCounts": NumberTag(code=325, type=16, length=1, value=49152),
            "SampleFormat": ListTag(code=339, type=3, length=3, value=[1, 1, 1]),
        },
    ]
    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            ifds = reader._ifds

    assert ifds == [
        IFD(pointer=16, n_tags=12, next_ifd_pointer=196880, tags=tags[0]),
        IFD(pointer=196880, n_tags=13, next_ifd_pointer=197156, tags=tags[1]),
        IFD(pointer=197156, n_tags=13, next_ifd_pointer=197432, tags=tags[2]),
        IFD(pointer=197432, n_tags=13, next_ifd_pointer=197708, tags=tags[3]),
        IFD(pointer=197708, n_tags=13, next_ifd_pointer=0, tags=tags[4]),
    ]


@pytest.mark.asyncio
async def test_fill_tag_data() -> None:
    url = "BigTIFF.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            tag = ListTag(code=258, type=3, length=3, data_pointer=170)
            await reader._fill_tag_with_data(tag)


@pytest.mark.asyncio
async def test_tag_fractional() -> None:
    url = "be_cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            tag = reader._ifds[0].tags["ReferenceBlackWhite"]
            await reader._fill_tag_with_data(tag)
            assert tag.value == [
                Fraction(0, 1),
                Fraction(255, 1),
                Fraction(128, 1),
                Fraction(255, 1),
                Fraction(128, 1),
                Fraction(255, 1),
            ]


@pytest.mark.asyncio
async def test_tag_ascii() -> None:
    url = "be_cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            tag = reader._ifds[1].tags["NewSubfileType"]
            await reader._fill_tag_with_data(tag)
            assert tag.value == "test"


@pytest.mark.asyncio
async def test_parse_geokeys() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            ifd = reader._ifds[5]

            await reader._fill_ifd_with_data(ifd)
            assert ifd["GTCitation"] == "WGS 84 / Pseudo-Mercator"
            assert ifd["GTModelType"] == 1
            assert ifd["GTRasterType"] == 1
            assert ifd["GeogCitation"] == "WGS 84"
            assert ifd["GeogPrimeMeridian"] == 1.3
            assert ifd["ProjLinearUnits"] == 37378
            assert ifd["ProjectedCSType"] == 3857


@pytest.mark.asyncio
async def test_ifd_iter() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert [ifd for ifd in reader] == [ifd for ifd in reader._ifds]
