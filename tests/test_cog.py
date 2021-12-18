# Thanks to mapbox/COGDumper for the mock data
from pathlib import Path
from typing import Any

import pytest
from aioresponses import CallbackResult, aioresponses

from async_cog import COGReader


def test_constructor() -> None:
    url = "http://example.com"
    reader = COGReader(url)

    assert reader.url == url


def response_read(url: str, **kwargs: Any) -> CallbackResult:
    path = (Path.cwd() / Path(__file__).parent).resolve()
    with open(path / "mock_data" / str(url), "rb") as file:
        range_header = kwargs["headers"]["Range"]
        offset, data_length = map(int, range_header.split("bytes=")[1].split("-"))
        file.seek(offset)
        data = file.read(data_length + 1)
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
