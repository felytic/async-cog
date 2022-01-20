# Thanks to mapbox/COGDumper for the mock data
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from aioresponses import CallbackResult, aioresponses

from async_cog import COGReader
from async_cog.geo_key import GeoKey
from async_cog.ifd import IFD
from async_cog.tag import Tag


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
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"@\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"@\x00"),
            "BitsPerSample": Tag(code=258, type=3, n_values=3, data_pointer=170),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x00\x01"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x00\x01"),
            "TileOffsets": Tag(code=324, type=4, n_values=1, data=b"\xff\x00\x00\x00"),
            "TileByteCounts": Tag(
                code=325, type=4, n_values=1, data=b"\xbb\x0f\x00\x00"
            ),
            "SampleFormat": Tag(code=339, type=3, n_values=3, data_pointer=176),
            "JPEGTables": Tag(code=347, type=7, n_values=73, data_pointer=182),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b" \x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b" \x00"),
            "BitsPerSample": Tag(code=258, type=3, n_values=3, data_pointer=4456),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(code=324, type=4, n_values=1, data=b"\xc9\x14\x00\x00"),
            "TileByteCounts": Tag(
                code=325, type=4, n_values=1, data=b"\xd7\x08\x00\x00"
            ),
            "SampleFormat": Tag(code=339, type=3, n_values=3, data_pointer=4462),
            "JPEGTables": Tag(code=347, type=7, n_values=73, data_pointer=4468),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"\x10\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"\x10\x00"),
            "BitsPerSample": Tag(code=258, type=3, n_values=3, data_pointer=4716),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(code=324, type=4, n_values=1, data=b"\xa0\x1d\x00\x00"),
            "TileByteCounts": Tag(
                code=325, type=4, n_values=1, data=b"\xe4\x03\x00\x00"
            ),
            "SampleFormat": Tag(code=339, type=3, n_values=3, data_pointer=4722),
            "JPEGTables": Tag(code=347, type=7, n_values=73, data_pointer=4728),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"\x08\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"\x08\x00"),
            "BitsPerSample": Tag(code=258, type=3, n_values=3, data_pointer=4976),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(code=324, type=4, n_values=1, data=b"\x84!\x00\x00"),
            "TileByteCounts": Tag(
                code=325, type=4, n_values=1, data=b"\xa7\x03\x00\x00"
            ),
            "SampleFormat": Tag(code=339, type=3, n_values=3, data_pointer=4982),
            "JPEGTables": Tag(code=347, type=7, n_values=73, data_pointer=4988),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"\x04\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"\x04\x00"),
            "BitsPerSample": Tag(code=258, type=3, n_values=3, data_pointer=5236),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x07\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(code=324, type=4, n_values=1, data=b"+%\x00\x00"),
            "TileByteCounts": Tag(code=325, type=4, n_values=1, data=b"&\x05\x00\x00"),
            "SampleFormat": Tag(code=339, type=3, n_values=3, data_pointer=5242),
            "JPEGTables": Tag(code=347, type=7, n_values=73, data_pointer=5248),
        },
        {
            "GeoKeyDirectoryTag": Tag(
                code=34735, type=3, n_values=32, data_pointer=10851
            )
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
                IFD(pointer=10833, n_tags=1, next_ifd_pointer=0, tags=tags[5]),
            ]


@pytest.mark.asyncio
async def test_read_ifds_big_tiff() -> None:
    url = "BigTIFF.tif"

    tags = [
        {
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"@\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"@\x00"),
            "BitsPerSample": Tag(
                code=258, type=3, n_values=3, data=b"\x08\x00\x08\x00\x08\x00"
            ),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x00\x01"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x00\x01"),
            "TileOffsets": Tag(
                code=324, type=16, n_values=1, data=b"\x10\x01\x00\x00\x00\x00\x00\x00"
            ),
            "TileByteCounts": Tag(
                code=325,
                type=16,
                n_values=1,
                data=b"\x00\x00\x03\x00\x00\x00\x00\x00",
            ),
            "SampleFormat": Tag(
                code=339, type=3, n_values=3, data=b"\x01\x00\x01\x00\x01\x00"
            ),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b" \x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b" \x00"),
            "BitsPerSample": Tag(
                code=258, type=3, n_values=3, data=b"\x08\x00\x08\x00\x08\x00"
            ),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(
                code=324, type=16, n_values=1, data=b"`\x05\x03\x00\x00\x00\x00\x00"
            ),
            "TileByteCounts": Tag(
                code=325, type=16, n_values=1, data=b"\x00\xc0\x00\x00\x00\x00\x00\x00"
            ),
            "SampleFormat": Tag(
                code=339, type=3, n_values=3, data=b"\x01\x00\x01\x00\x01\x00"
            ),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"\x10\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"\x10\x00"),
            "BitsPerSample": Tag(
                code=258, type=3, n_values=3, data=b"\x08\x00\x08\x00\x08\x00"
            ),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(
                code=324, type=16, n_values=1, data=b"`\xc5\x03\x00\x00\x00\x00\x00"
            ),
            "TileByteCounts": Tag(
                code=325, type=16, n_values=1, data=b"\x00\xc0\x00\x00\x00\x00\x00\x00"
            ),
            "SampleFormat": Tag(
                code=339, type=3, n_values=3, data=b"\x01\x00\x01\x00\x01\x00"
            ),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"\x08\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"\x08\x00"),
            "BitsPerSample": Tag(
                code=258, type=3, n_values=3, data=b"\x08\x00\x08\x00\x08\x00"
            ),
            "Compression": Tag(code=259, type=3, n_values=1, data=b"\x01\x00"),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(
                code=324, type=16, n_values=1, data=b"`\x85\x04\x00\x00\x00\x00\x00"
            ),
            "TileByteCounts": Tag(
                code=325, type=16, n_values=1, data=b"\x00\xc0\x00\x00\x00\x00\x00\x00"
            ),
            "SampleFormat": Tag(
                code=339, type=3, n_values=3, data=b"\x01\x00\x01\x00\x01\x00"
            ),
        },
        {
            "NewSubfileType": Tag(
                code=254, type=4, n_values=1, data=b"\x01\x00\x00\x00"
            ),
            "ImageWidth": Tag(code=256, type=3, n_values=1, data=b"\x04\x00"),
            "ImageLength": Tag(code=257, type=3, n_values=1, data=b"\x04\x00"),
            "BitsPerSample": Tag(
                code=258, type=3, n_values=3, data=b"\x08\x00\x08\x00\x08\x00"
            ),
            "Compression": Tag(
                code=259,
                type=3,
                n_values=1,
                data=b"\x01\x00",
            ),
            "PhotometricInterpretation": Tag(
                code=262, type=3, n_values=1, data=b"\x02\x00"
            ),
            "SamplesPerPixel": Tag(code=277, type=3, n_values=1, data=b"\x03\x00"),
            "PlanarConfiguration": Tag(code=284, type=3, n_values=1, data=b"\x01\x00"),
            "TileWidth": Tag(code=322, type=3, n_values=1, data=b"\x80\x00"),
            "TileLength": Tag(code=323, type=3, n_values=1, data=b"\x80\x00"),
            "TileOffsets": Tag(
                code=324, type=16, n_values=1, data=b"`E\x05\x00\x00\x00\x00\x00"
            ),
            "TileByteCounts": Tag(
                code=325, type=16, n_values=1, data=b"\x00\xc0\x00\x00\x00\x00\x00\x00"
            ),
            "SampleFormat": Tag(
                code=339, type=3, n_values=3, data=b"\x01\x00\x01\x00\x01\x00"
            ),
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
            tag = Tag(code=258, type=3, n_values=3, data_pointer=170)
            await reader._fill_tag_with_data(tag)
            assert tag.data == b"\x00\x00\x00\x00\x00\x00"

            filled_tag = Tag(code=259, type=3, n_values=1, data=b"\x01\x00")
            await reader._fill_tag_with_data(filled_tag)
            assert filled_tag == Tag(
                code=259, type=3, n_values=1, data=b"\x01\x00", values=[1]
            )

            tag_without_data = Tag(code=259, type=3, n_values=1)
            await reader._fill_tag_with_data(tag_without_data)


@pytest.mark.asyncio
async def test_tag_fractional() -> None:
    url = "be_cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            tag = reader._ifds[0].tags["ReferenceBlackWhite"]
            await reader._fill_tag_with_data(tag)
            assert tag.values == [
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
            tag = reader._ifds[5].tags["GeoKeyDirectoryTag"]
            await reader._fill_tag_with_data(tag)
            assert tag.value == [
                GeoKey(code=1024, tag_location=0, count=1, value=1),
                GeoKey(code=1025, tag_location=0, count=1, value=1),
                GeoKey(code=1026, tag_location=34737, count=25, value=0),
                GeoKey(code=2049, tag_location=34737, count=7, value=25),
                GeoKey(code=2054, tag_location=0, count=1, value=9102),
                GeoKey(code=3072, tag_location=0, count=1, value=3857),
                GeoKey(code=3076, tag_location=0, count=4096, value=37378),
            ]
