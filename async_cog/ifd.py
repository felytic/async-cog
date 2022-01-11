from struct import calcsize
from typing import List, Optional

from pydantic import BaseModel, validator


class Tag(BaseModel):
    code: int
    type: int
    n_values: int
    data_pointer: Optional[int]
    data: Optional[bytes]

    @validator("type")
    def validate_type(cls, type_code: int) -> int:
        if type_code not in TAG_TYPES:
            raise ValueError(f"Tag with type {type_code} is not supported")

        return type_code

    @property
    def format(self) -> str:
        return f"{self.n_values}{TAG_TYPES[self.type]}"

    @property
    def data_size(self) -> int:
        return calcsize(self.format)

    @property
    def name(self) -> str:
        return TAG_NAMES.get(self.code, "UNKNOWN")


class IFD(BaseModel):
    pointer: int
    n_tags: int
    next_ifd_pointer: int
    tags: List[Tag]


# https://docs.python.org/3/library/struct.html#format-characters
TAG_TYPES = {
    1: "B",  # BYTE
    2: "c",  # ASCII
    3: "H",  # SHORT
    4: "I",  # LONG
    # FIXME In TIFF format, a RATIONAL value is a fractional value
    # represented by the ratio of two unsigned 4-byte integers.
    5: "Q",  # RATIONAL
    6: "b",  # SBYTE
    7: "c",  # UNDEFINED
    8: "h",  # SSHORT
    9: "i",  # SLONG
    # FIXME same for signed RATIONAL
    10: "q",  # SRATIONAL
    11: "f",  # FLOAT
    12: "d",  # DOUBLE
    16: "Q",  # LONG8
}


# https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html
# https://svn.osgeo.org/metacrs/geotiff/trunk/geotiff/html/usgs_geotiff.html#hdr%2054
TAG_NAMES = {
    254: "NewSubfileType",
    255: "SubfileType",
    256: "ImageWidth",
    257: "ImageLength",
    258: "BitsPerSample",
    259: "Compression",
    262: "PhotometricInterpretation",
    263: "Threshholding",
    264: "CellWidth",
    265: "CellLength",
    266: "FillOrder",
    270: "ImageDescription",
    271: "Make",
    272: "Model",
    273: "StripOffsets",
    274: "Orientation",
    277: "SamplesPerPixel",
    278: "RowsPerStrip",
    279: "StripByteCounts",
    280: "MinSampleValue",
    281: "MaxSampleValue",
    282: "XResolution",
    283: "YResolution",
    284: "PlanarConfiguration",
    288: "FreeOffsets",
    289: "FreeByteCounts",
    290: "GrayResponseUnit",
    291: "GrayResponseCurve",
    296: "ResolutionUnit",
    305: "Software",
    306: "DateTime",
    315: "Artist",
    316: "HostComputer",
    320: "ColorMap",
    338: "ExtraSamples",
    33432: "Copyright",
    33550: "ModelPixelScaleTag",
    33920: "ModelTransformationTag",
    33922: "ModelTiepointTag",
    34735: "GeoKeyDirectoryTag",
    34736: "GeoDoubleParamsTag",
    34737: "GeoAsciiParamsTag",
}
