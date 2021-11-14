from async_cog import COGReader


def test_constructor():
    url = "http://example.com"
    reader = COGReader(url)

    assert reader.url == url
