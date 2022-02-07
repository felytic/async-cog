from pytest import raises

from async_cog.tags import Tag


def test_tag_format() -> None:
    tag = Tag(code=254, type=4, n_values=13)
    assert tag.format_str == "13I"
    assert tag.data_pointer is None


def test_tag_size() -> None:
    tag = Tag(code=254, type=4, n_values=13)
    assert tag.data_size == 52


def test_tag_name() -> None:
    tag = Tag(code=34735, type=3, n_values=32, data_pointer=502)
    assert tag.name == "GeoKeyDirectoryTag"


def test_tag_str() -> None:
    tag = Tag(code=34735, type=3, n_values=32, data_pointer=502)
    assert str(tag) == "GeoKeyDirectoryTag: None"

    tag = Tag(code=257, type=3, n_values=1, value=256)
    assert str(tag) == "ImageLength: 256"

    tag = Tag(code=258, type=3, n_values=3, value=[8, 8, 8])
    assert str(tag) == "BitsPerSample: [8, 8, 8]"


def test_not_imlemented() -> None:
    tag = Tag(code=34735, type=3, n_values=32, data_pointer=502)

    with raises(NotImplementedError):
        tag.parse_data(b"", "<")
