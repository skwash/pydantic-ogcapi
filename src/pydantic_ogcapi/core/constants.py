"""Well-known URIs defined by the OGC API - Features standards."""

#: Default coordinate reference system for 2D geometries (WGS 84 longitude/latitude).
CRS84 = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"

#: Coordinate reference system for 3D geometries (WGS 84 longitude/latitude/height).
CRS84h = "http://www.opengis.net/def/crs/OGC/0/CRS84h"

#: Default temporal reference system (the Gregorian calendar, per ISO 8601).
GREGORIAN_TRS = "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"

# Part 1: Core conformance classes.
CONF_CORE = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core"
CONF_OAS30 = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30"
CONF_HTML = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html"
CONF_GEOJSON = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
CONF_GMLSF0 = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/gmlsf0"
CONF_GMLSF2 = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/gmlsf2"

# Part 2: Coordinate Reference Systems by Reference.
CONF_CRS = "http://www.opengis.net/spec/ogcapi-features-2/1.0/conf/crs"

# Part 3: Filtering.
CONF_QUERYABLES = "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/queryables"
CONF_QUERYABLES_QUERY_PARAMETERS = (
    "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/queryables-query-parameters"
)
CONF_FILTER = "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter"
CONF_FEATURES_FILTER = "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/features-filter"

# CQL2 (OGC 21-065r2), advertised alongside Part 3.
CONF_CQL2_TEXT = "http://www.opengis.net/spec/cql2/1.0/conf/cql2-text"
CONF_CQL2_JSON = "http://www.opengis.net/spec/cql2/1.0/conf/cql2-json"
CONF_BASIC_CQL2 = "http://www.opengis.net/spec/cql2/1.0/conf/basic-cql2"

# Part 4: Create, Replace, Update and Delete.
CONF_CREATE_REPLACE_DELETE = (
    "http://www.opengis.net/spec/ogcapi-features-4/1.0/conf/create-replace-delete"
)
CONF_UPDATE = "http://www.opengis.net/spec/ogcapi-features-4/1.0/conf/update"
CONF_TRANSACTION_FEATURES = "http://www.opengis.net/spec/ogcapi-features-4/1.0/conf/features"
