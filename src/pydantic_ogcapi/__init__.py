"""Pydantic models for the OGC API - Features standards.

This package extends `pydantic-geojson <https://pypi.org/project/pydantic-geojson/>`_
with the objects defined by OGC API - Features. Each part of the standard lives
in its own module, and every public name is re-exported here, so that a caller
can work from a single import::

    from pydantic_ogcapi import Collection, Feature, FeatureCollection

The per-part modules remain importable when that is clearer::

    from pydantic_ogcapi.core import LandingPage
    from pydantic_ogcapi.filtering import Queryables

Models declare snake_case attributes and serialise to the camelCase (and, for
some query parameters, kebab-case) member names the standards define. Both
spellings are accepted when parsing, and ``model_dump()`` emits the wire names
and omits members that are not set.

Modules:
    core: Part 1, Core — landing page, conformance, collections and features.
    crs: Part 2, Coordinate Reference Systems by Reference.
    filtering: Part 3, Filtering — queryables, CQL2 functions and parameters.
    transaction: Part 4, Create, Replace, Update and Delete.
"""

from ._base import OGCModel
from .core import (
    CONF_CORE,
    CONF_GEOJSON,
    CONF_GMLSF0,
    CONF_GMLSF2,
    CONF_HTML,
    CONF_OAS30,
    CRS84,
    OPEN_ENDED,
    BoundingBox,
    Collection,
    Collections,
    ConformanceDeclaration,
    CRS84h,
    DatetimeInterval,
    Exception_,
    Extent,
    Feature,
    FeatureCollection,
    LandingPage,
    Link,
    OGCException,
    SpatialExtent,
    TemporalExtent,
)
from .core.constants import GREGORIAN_TRS
from .crs import CONF_CRS, CrsParameters, format_content_crs, parse_content_crs
from .filtering import (
    CONF_BASIC_CQL2,
    CONF_CQL2_JSON,
    CONF_CQL2_TEXT,
    CONF_FEATURES_FILTER,
    CONF_FILTER,
    CONF_QUERYABLES,
    CONF_QUERYABLES_QUERY_PARAMETERS,
    QUERYABLES_SCHEMA_DIALECT,
    FilterLang,
    FilterParameters,
    Function,
    FunctionArgument,
    Functions,
    Queryable,
    Queryables,
    QueryableType,
)
from .transaction import (
    CONF_CREATE_REPLACE_DELETE,
    CONF_TRANSACTION_FEATURES,
    CONF_UPDATE,
    ConditionalHeaders,
    TransactionResponse,
    TransactionStatus,
)

__version__ = "0.1.0"

__all__ = [
    # Base
    "OGCModel",
    # Part 1: Core
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
    # Part 2: CRS
    "CrsParameters",
    "format_content_crs",
    "parse_content_crs",
    # Part 3: Filtering
    "FilterLang",
    "FilterParameters",
    "Function",
    "FunctionArgument",
    "Functions",
    "Queryable",
    "QueryableType",
    "Queryables",
    # Part 4: Transactions
    "ConditionalHeaders",
    "TransactionResponse",
    "TransactionStatus",
    # Well-known URIs
    "CRS84",
    "CRS84h",
    "GREGORIAN_TRS",
    "OPEN_ENDED",
    "QUERYABLES_SCHEMA_DIALECT",
    # Conformance classes
    "CONF_BASIC_CQL2",
    "CONF_CORE",
    "CONF_CQL2_JSON",
    "CONF_CQL2_TEXT",
    "CONF_CREATE_REPLACE_DELETE",
    "CONF_CRS",
    "CONF_FEATURES_FILTER",
    "CONF_FILTER",
    "CONF_GEOJSON",
    "CONF_GMLSF0",
    "CONF_GMLSF2",
    "CONF_HTML",
    "CONF_OAS30",
    "CONF_QUERYABLES",
    "CONF_QUERYABLES_QUERY_PARAMETERS",
    "CONF_TRANSACTION_FEATURES",
    "CONF_UPDATE",
    "__version__",
]
