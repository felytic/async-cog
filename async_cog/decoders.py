from typing import Any, Callable, Dict

import numpy as np
from imagecodecs import jpeg_decode

from async_cog.ifd import IFD


def decode_raw(ifd: IFD, data: bytes) -> np.ndarray:
    bits_per_sample = ifd["BitsPerSample"]
    width = ifd["TileWidth"]
    height = ifd["TileHeight"]

    shape = (width, height, len(bits_per_sample))

    bytes_per_samples = bits_per_sample[0] // 8

    # E.g 8 bits per sample will be "u1"
    dtype = np.dtype(f"u{bytes_per_samples}")

    return np.frombuffer(data, dtype=dtype).reshape(*shape)


def decode_jpeg(ifd: IFD, data: bytes) -> np.ndarray:
    jpeg_table = ifd["JPEGTables"]

    # insert tables, first removing the SOI and EOI
    data = data[0:2] + jpeg_table[2:-2] + data[2:]

    return jpeg_decode(data)


Decoder = Callable[[IFD, bytes], Any]

DECODERS_MAPPING: Dict[int, Decoder] = {
    1: decode_raw,
    6: decode_jpeg,
    7: decode_jpeg,
}
