from typing import Any, Callable, Dict

import numpy as np

from async_cog.ifd import IFD


def decode_raw(ifd: IFD, data: bytes) -> Any:
    bits_per_sample = ifd["BitsPerSample"]
    width = ifd["TileWidth"]
    height = ifd["TileHeight"]

    shape = (width, height, len(bits_per_sample))

    bytes_per_samples = bits_per_sample[0] // 8

    # E.g 8 bits per sample will be "u1"
    dtype = np.dtype(f"u{bytes_per_samples}")

    return np.frombuffer(data, dtype=dtype).reshape(*shape)


Decoder = Callable[[IFD, bytes], Any]

DECODERS_MAPPING: Dict[int, Decoder] = {
    1: decode_raw,
}
