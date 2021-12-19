# Thanks to mapbox/COGDumper for the mock data
from pathlib import Path
from typing import Any

import pytest
from aioresponses import CallbackResult, aioresponses

from async_cog import COGReader
from async_cog.ifd import IFD


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
                IFD(offset=8, n_entries=13, next_ifd_pointer=4282),
                IFD(offset=4282, n_entries=14, next_ifd_pointer=4542),
                IFD(offset=4542, n_entries=14, next_ifd_pointer=4802),
                IFD(offset=4802, n_entries=14, next_ifd_pointer=5062),
                IFD(offset=5062, n_entries=14, next_ifd_pointer=0),
            ]


@pytest.mark.asyncio
async def test_read_ifds_big_tiff() -> None:
    url = "BigTIFF.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert reader._ifds == [
                IFD(offset=16, n_entries=12, next_ifd_pointer=196880),
                IFD(offset=196880, n_entries=13, next_ifd_pointer=197156),
                IFD(offset=197156, n_entries=13, next_ifd_pointer=197432),
                IFD(offset=197432, n_entries=13, next_ifd_pointer=197708),
                IFD(offset=197708, n_entries=13, next_ifd_pointer=0),
            ]
