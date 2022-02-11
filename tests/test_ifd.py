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
                "ImageHeight": 64,
                "ImageWidth": 64,
                "SampleFormat": [1, 1, 1],
                "SamplesPerPixel": 3,
                "TileByteCounts": [4027],
                "TileHeight": 256,
                "TileOffsets": [255],
                "TileWidth": 256,
                "UNKNOWN TAG 8476": [1],
            }


@pytest.mark.asyncio
async def test_ifd_dict_methods() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            ifd = reader._ifds[0]
            assert ifd["SamplesPerPixel"] == 3
            assert ifd.get("SamplesPerPixel") == 3

            tag = Tag(code=34735, type=3, length=32, data_pointer=10851)
            ifd["GeoKeyDirectoryTag"] = tag

            with pytest.raises(AssertionError):
                ifd["Wrong name"] = tag

            assert "ImageWidth" in ifd
            assert "Wrong key" not in ifd
            assert ifd.get("Wrong key") is None
            assert ifd.get("Wrong key", "default") == "default"


@pytest.mark.asyncio
async def test_ifd_xy_tile_counts() -> None:
    url = "cog.tif"

    with aioresponses() as mocked_response:
        mocked_response.get(url, callback=response_read, repeat=True)

        async with COGReader(url) as reader:
            ifd_0 = reader._ifds[0]
            assert ifd_0.x_tile_count == 1
            assert ifd_0.y_tile_count == 1

            ifd_5 = reader._ifds[5]  # IFD without TileWidth and ImageWidth properties
            assert ifd_5.x_tile_count == 0
            assert ifd_5.y_tile_count == 0
