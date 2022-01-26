from typing import Any, Optional

from pydantic import BaseModel


class GeoKey(BaseModel):
    code: int
    tag_code: int
    length: int
    value: Optional[Any]
    offset: Optional[int]

    def __str__(self) -> str:
        return f"{self.name}: {str(self.value)}"

    @property
    def name(self) -> str:
        return GEO_KEY_NAMES.get(self.code, f"UNKNOWN KEY {self.code}")


# https://svn.osgeo.org/metacrs/geotiff/trunk/geotiff/html/usgs_geotiff.html#hdr%2055
GEO_KEY_NAMES = {
    1024: "GTModelType",
    1025: "GTRasterType",
    1026: "GTCitation",
    2048: "GeographicType",
    2049: "GeogCitation",
    2050: "GeogGeodeticDatum",
    2051: "GeogPrimeMeridian",
    2052: "GeogLinearUnits",
    2053: "GeogLinearUnitSize",
    2054: "GeogAngularUnits",
    2055: "GeogAngularUnitSize",
    2056: "GeogEllipsoid",
    2057: "GeogSemiMajorAxis",
    2058: "GeogSemiMinorAxis",
    2059: "GeogInvFlattening",
    2060: "GeogAzimuthUnits",
    2061: "GeogPrimeMeridianLong",
    3072: "ProjectedCSType",
    3073: "PCSCitation",
    3074: "Projection",
    3075: "ProjCoordTrans",
    3076: "ProjLinearUnits",
    3077: "ProjLinearUnitSize",
    3078: "ProjStdParallel",
    3079: "ProjStdParallel2",
    3080: "ProjOriginLong",
    3081: "ProjOriginLat",
    3082: "ProjFalseEasting",
    3083: "ProjFalseNorthing",
    3084: "ProjFalseOriginLong",
    3085: "ProjFalseOriginLat",
    3086: "ProjFalseOriginEasting",
    3087: "ProjFalseOriginNorthing",
    3088: "ProjCenterLong",
    3089: "ProjCenterLat",
    3090: "ProjCenterEasting",
    3091: "ProjCenterNorthing",
    3092: "ProjScaleAtOrigin",
    3093: "ProjScaleAtCenter",
    3094: "ProjAzimuthAngle",
    3095: "ProjStraightVertPoleLong",
}
