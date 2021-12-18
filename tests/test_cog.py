# Thanks to mapbox/COGDumper for the mock data
from pathlib import Path

import pytest
from aioresponses import CallbackResult, aioresponses

from async_cog import COGReader


def test_constructor():
    url = "http://example.com"
    reader = COGReader(url)

    assert reader.url == url


def response_read(url, **kwargs) -> CallbackResult:
    path = (Path.cwd() / Path(__file__).parent).resolve()
    with open(path / "mock_data" / "cog.tif", "rb") as file:
        range_header = kwargs["headers"]["Range"]
        offset, data_length = map(int, range_header.split("bytes=")[1].split("-"))
        file.seek(offset)
        data = file.read(data_length + 1)
        return CallbackResult(body=data, content_type="image/tiff")


@pytest.mark.asyncio
async def test_read_header():
    url = "http://cog.test/cog.tiff"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert not reader.is_bigtiff
