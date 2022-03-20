from __future__ import annotations

from typing import Any, Iterator


class TagCode(int):
    name: str
    is_list: bool

    # pydantic needs this function for validation, see:
    # https://pydantic-docs.helpmanual.io/usage/types/#classes-with-__get_validators__
    @classmethod
    def __get_validators__(cls) -> Iterator[Any]:
        yield cls.validate

    @classmethod
    def validate(cls, code: int) -> TagCode:
        return cls(code)

    def __init__(self, code: int):
        if code in SINGLE_VALUE_TAGS_NAMES:
            self.name = SINGLE_VALUE_TAGS_NAMES[code]
            self.is_list = False

        elif code in LIST_TAG_NAMES:
            self.name = LIST_TAG_NAMES[code]
            self.is_list = True

        else:
            self.name = f"UNKNOWN TAG {code}"
            self.is_list = True


# https://www.awaresystems.be/imaging/tiff/tifftags/baseline.html
# https://svn.osgeo.org/metacrs/geotiff/trunk/geotiff/html/usgs_geotiff.html#hdr%2054
# https://github.com/python-pillow/Pillow/blob/main/src/PIL/TiffTags.py#L78
SINGLE_VALUE_TAGS_NAMES = {
    254: "NewSubfileType",
    255: "SubfileType",
    256: "ImageWidth",
    257: "ImageHeight",
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
    274: "Orientation",
    277: "SamplesPerPixel",
    278: "RowsPerStrip",
    282: "XResolution",
    283: "YResolution",
    284: "PlanarConfiguration",
    285: "PageName",
    286: "XPosition",
    287: "YPosition",
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
    322: "TileWidth",
    323: "TileHeight",
    332: "InkSet",
    333: "InkNames",
    334: "NumberOfInks",
    336: "DotRange",
    337: "TargetPrinter",
    340: "SMinSampleValue",
    341: "SMaxSampleValue",
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
    531: "YCbCrPositioning",
    700: "XMP",
    33432: "Copyright",
}

LIST_TAG_NAMES = {
    258: "BitsPerSample",
    273: "StripOffsets",
    279: "StripByteCounts",
    280: "MinSampleValue",
    281: "MaxSampleValue",
    288: "FreeOffsets",
    289: "FreeByteCounts",
    320: "ColorMap",
    321: "HalftoneHints",
    324: "TileOffsets",
    325: "TileByteCounts",
    338: "ExtraSamples",
    339: "SampleFormat",
    342: "TransferRange",
    529: "YCbCrCoefficients",
    530: "YCbCrSubSampling",
    532: "ReferenceBlackWhite",
    33550: "ModelPixelScaleTag",
    33920: "ModelTransformationTag",
    33922: "ModelTiepointTag",
    34735: "GeoKeyDirectoryTag",
    34736: "GeoDoubleParamsTag",
    34737: "GeoAsciiParamsTag",
}


GEOKEY_TAGS = [34735, 34736, 34737]
