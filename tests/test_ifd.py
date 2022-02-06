import pytest
from aioresponses import aioresponses

from async_cog import COGReader
from async_cog.tags import Tag
from tests.test_cog_reader import response_read


@pytest.mark.asyncio
async def test_ifd_to_dict() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            await reader._fill_ifd_with_data(reader._ifds[0])

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
async def test_ifd_dict_methods() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            ifd = reader._ifds[0]
            assert ifd["SamplesPerPixel"] == 3

            tag = Tag(code=34735, type=3, n_values=32, data_pointer=10851)
            ifd["GeoKeyDirectoryTag"] = tag

        with pytest.raises(AssertionError):
            ifd["Wrong name"] = tag

        assert "ImageWidth" in ifd
        assert "Wrong key" not in ifd
