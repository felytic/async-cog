from pathlib import Path
from typing import Any, Callable, Generator

from aioresponses import CallbackResult, aioresponses
from pytest import fixture

from async_cog import COGReader


def response_read(url: str, **kwargs: Any) -> CallbackResult:
    path = (Path.cwd() / Path(__file__).parent).resolve()

    with open(path / "mock_data" / str(url), "rb") as file:
        range_header = kwargs["headers"]["Range"]
        offset_start, offset_end = map(int, range_header.split("bytes=")[1].split("-"))
        file.seek(offset_start)
        data = file.read(offset_end - offset_start + 1)
        return CallbackResult(body=data, content_type="image/tiff")


@fixture
def mocked_reader() -> Generator[Callable[[str], COGReader], Any, Any]:
    with aioresponses() as mocked_response:

        def _get_mocked_reader(url: str) -> COGReader:
            mocked_response.get(url, callback=response_read, repeat=True)

            return COGReader(url)

        yield _get_mocked_reader
