from async_cog.geo_key import GeoKey


def test_geokey_name() -> None:
    key = GeoKey(code=1024, tag_location=0, count=1, value=1)

    assert key.name == "GTModelType"
    assert str(key) == "GTModelType: 1"
