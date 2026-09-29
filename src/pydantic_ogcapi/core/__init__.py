"""Part 1: Core — the landing page, collections and GeoJSON feature objects."""

from .collection import (
    Collection,
    Collections,
    ConformanceDeclaration,
    Extent,
    LandingPage,
    SpatialExtent,
    TemporalExtent,
)
from .constants import (
    CONF_CORE,
    CONF_GEOJSON,
    CONF_GMLSF0,
    CONF_GMLSF2,
    CONF_HTML,
    CONF_OAS30,
    CRS84,
    GREGORIAN_TRS,
    CRS84h,
)
from .exception import Exception_, OGCException
from .features import Feature, FeatureCollection
from .link import Link
from .parameters import OPEN_ENDED, BoundingBox, DatetimeInterval

__all__ = [
    "CONF_CORE",
    "CONF_GEOJSON",
    "CONF_GMLSF0",
    "CONF_GMLSF2",
    "CONF_HTML",
    "CONF_OAS30",
    "CRS84",
    "CRS84h",
    "GREGORIAN_TRS",
    "OPEN_ENDED",
    "BoundingBox",
    "Collection",
    "Collections",
    "ConformanceDeclaration",
    "DatetimeInterval",
    "Exception_",
    "Extent",
    "Feature",
    "FeatureCollection",
    "LandingPage",
    "Link",
    "OGCException",
    "SpatialExtent",
    "TemporalExtent",
]
