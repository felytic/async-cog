from pytest import mark


@mark.asyncio
async def test_decode_uncompressed(mocked_reader) -> None:
    async with mocked_reader("cog.tif") as reader:
        data = await reader._read_tile_data(0, 0, 0)
        assert isinstance(data, bytes)
        assert len(data) == 4027
