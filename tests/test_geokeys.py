from async_cog.geokeys import GeoKey


def test_geokey_name() -> None:
    key = GeoKey(code=1024, value=1)

    assert key.name == "GTModelType"
    assert str(key) == "GTModelType: 1"
