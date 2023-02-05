from typing import Any, Callable, Dict

import numpy as np
from imagecodecs import delta_decode, jpeg_decode, lzw_decode

from async_cog.ifd import IFD


def decode_raw(ifd: IFD, data: bytes) -> np.ndarray:
    return np.frombuffer(data, dtype=ifd.numpy_dtype).reshape(*ifd.numpy_shape)


def decode_lzw(ifd: IFD, data: bytes) -> np.ndarray:
    uncompressed_data = lzw_decode(data)
    array = np.frombuffer(uncompressed_data, dtype=ifd.numpy_dtype).reshape(
        *ifd.numpy_shape
    )

    if ifd.get("Predictor") == 2:
        delta_decode(array, out=array, axis=-1)

    return array


def decode_jpeg(ifd: IFD, data: bytes) -> np.ndarray:
    jpeg_table = ifd["JPEGTables"]

    # insert tables, first removing the SOI and EOI
    data = data[0:2] + jpeg_table[2:-2] + data[2:]

    return jpeg_decode(data)


Decoder = Callable[[IFD, bytes], Any]

DECODERS_MAPPING: Dict[int, Decoder] = {
    1: decode_raw,
    5: decode_lzw,
    6: decode_jpeg,
    7: decode_jpeg,
}
