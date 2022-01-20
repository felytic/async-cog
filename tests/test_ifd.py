import pytest
from aioresponses import aioresponses

from async_cog import COGReader
from async_cog.tag import Tag
from tests.test_cog_reader import response_read


@pytest.mark.asyncio
async def test_ifd_to_dict() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            await reader._fill_tags_with_data()

            assert reader._ifds[0].to_dict() == {
                "BitsPerSample": [8, 8, 8],
                "Compression": 7,
                "ImageLength": 64,
                "ImageWidth": 64,
                "PlanarConfiguration": 1,
                "SampleFormat": [1, 1, 1],
                "SamplesPerPixel": 3,
                "TileByteCounts": 4027,
                "TileLength": 256,
                "TileOffsets": 255,
                "TileWidth": 256,
            }


@pytest.mark.asyncio
async def test_ifd_get_and_set_item() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            assert reader._ifds[0]["SamplesPerPixel"] == b"\x03\x00"

            tag = Tag(code=34735, type=3, n_values=32, data_pointer=10851)
            reader._ifds[0]["GeoKeyDirectoryTag"] = tag

        with pytest.raises(AssertionError):
            reader._ifds[0]["Wrong name"] = tag
