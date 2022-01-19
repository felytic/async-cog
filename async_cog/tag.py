from fractions import Fraction
from struct import calcsize, unpack
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, validator

from async_cog.geo_key import GeoKey


class Tag(BaseModel):
    code: int
    type: int
    n_values: int
    data_pointer: Optional[int]
    data: Optional[bytes]
    values: Optional[List[Any]]

    def __str__(self) -> str:
        return f"{self.name}: {str(self.value)}"

    @validator("type")
    def validate_type(cls, type_code: int) -> int:
        if type_code not in TAG_TYPES:
            raise ValueError(f"Tag with type {type_code} is not supported")

        return type_code

    @property
    def format_str(self) -> str:
        return f"{self.n_values}{TAG_TYPES[self.type]}"

    @property
    def data_size(self) -> int:
        return calcsize(self.format_str)

    @property
    def name(self) -> str:
        return TAG_NAMES.get(self.code, f"UNKNOWN TAG {self.code}")

    @property
    def value(self) -> Union[Any, List[Any]]:
        if self.values:
            if len(self.values) == 1:
                return self.values[0]
            return self.values

        return self.data

    def parse_data(self, byte_order_fmt: Literal["<", ">"]) -> None:
        if self.type in (5, 10):  # RATIONAL and SIGNED RATIONAL
            self._parse_rationals(byte_order_fmt)

        elif self.type == 2:  # ASCII string
            self._parse_ascii(byte_order_fmt)

        else:
            self._parse(byte_order_fmt)

        if self.name == "GeoKeyDirectoryTag":
            self._parse_geokeys()

    def _parse(self, byte_order_fmt: Literal["<", ">"]) -> None:
        assert self.data
        self.values = list(unpack(f"{byte_order_fmt}{self.format_str}", self.data))

    def _parse_rationals(self, byte_order_fmt: Literal["<", ">"]) -> None:
        assert self.data
        type_str = "I" if self.type == 5 else "i"

        # two unsigned LONGs:  numerator and denominator
        format_str = f"{byte_order_fmt}{self.n_values * 2}{type_str}"
        values = unpack(format_str, self.data)
        numerators = values[::2]
        denominators = values[1::2]

        self.values = [
            Fraction(numerator, denominator)
            for numerator, denominator in zip(numerators, denominators)
        ]

    def _parse_ascii(self, byte_order_fmt: Literal["<", ">"]) -> None:
        assert self.data

        format_str = f"{byte_order_fmt}{self.format_str}"
        (bytes_str,) = unpack(format_str, self.data)
        self.values = bytes_str.decode().split("|")

    def _parse_geokeys(self) -> None:
        if self.values and len(self.values) >= 4:
            version, _, _, keys_n = self.values[:4]
            assert version == 1

            geo_keys = []

            for i in range(1, keys_n + 1):
                code, tag_location, count, value = self.values[4 * i : 4 * (i + 1)]
                geo_key = GeoKey(
                    code=code,
                    tag_location=tag_location,
                    count=count,
                    value=value,
                )

                geo_keys.append(geo_key)

            self.values = geo_keys


# https://docs.python.org/3/library/struct.html#format-characters
TAG_TYPES = {
    1: "B",  # BYTE
    2: "s",  # ASCII
    3: "H",  # SHORT
    4: "I",  # LONG
    # In TIFF format, a RATIONAL value is a fractional value
    # represented by the ratio of two unsigned 4-byte integers.
    5: "Q",  # RATIONAL
    6: "b",  # SBYTE
    7: "s",  # UNDEFINED
    8: "h",  # SSHORT
    9: "i",  # SLONG
    # same for signed RATIONAL
    10: "q",  # SRATIONAL
    11: "f",  # FLOAT
    12: "d",  # DOUBLE
    16: "Q",  # LONG8
}


# https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html
# https://svn.osgeo.org/metacrs/geotiff/trunk/geotiff/html/usgs_geotiff.html#hdr%2054
# https://github.com/python-pillow/Pillow/blob/main/src/PIL/TiffTags.py#L78
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
    269: "DocumentName",
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
    285: "PageName",
    286: "XPosition",
    287: "YPosition",
    288: "FreeOffsets",
    289: "FreeByteCounts",
    290: "GrayResponseUnit",
    291: "GrayResponseCurve",
    292: "T4Options",
    293: "T6Options",
    296: "ResolutionUnit",
    297: "PageNumber",
    301: "TransferFunction",
    305: "Software",
    306: "DateTime",
    315: "Artist",
    316: "HostComputer",
    317: "Predictor",
    318: "WhitePoint",
    319: "PrimaryChromaticities",
    320: "ColorMap",
    321: "HalftoneHints",
    322: "TileWidth",
    323: "TileLength",
    324: "TileOffsets",
    325: "TileByteCounts",
    332: "InkSet",
    333: "InkNames",
    334: "NumberOfInks",
    336: "DotRange",
    337: "TargetPrinter",
    338: "ExtraSamples",
    339: "SampleFormat",
    340: "SMinSampleValue",
    341: "SMaxSampleValue",
    342: "TransferRange",
    347: "JPEGTables",
    512: "JPEGProc",
    513: "JPEGInterchangeFormat",
    514: "JPEGInterchangeFormatLength",
    515: "JPEGRestartInterval",
    517: "JPEGLosslessPredictors",
    518: "JPEGPointTransforms",
    519: "JPEGQTables",
    520: "JPEGDCTables",
    521: "JPEGACTables",
    529: "YCbCrCoefficients",
    530: "YCbCrSubSampling",
    531: "YCbCrPositioning",
    532: "ReferenceBlackWhite",
    700: "XMP",
    33432: "Copyright",
    33550: "ModelPixelScaleTag",
    33920: "ModelTransformationTag",
    33922: "ModelTiepointTag",
    34735: "GeoKeyDirectoryTag",
    34736: "GeoDoubleParamsTag",
    34737: "GeoAsciiParamsTag",
}
