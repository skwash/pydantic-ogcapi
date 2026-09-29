"""Queryables and filtering models.

Reference: OGC 19-079r2 (OGC API - Features - Part 3: Filtering) and
OGC 21-065r2 (Common Query Language, CQL2)
"""

from enum import Enum
from typing import Any, Optional

from pydantic import Field

from .._base import OGCModel

#: The JSON Schema dialect used by a queryables resource.
QUERYABLES_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


class FilterLang(str, Enum):
    """The filter languages a service may accept in the ``filter-lang`` parameter.

    Attributes:
        cql2_text: The text encoding of CQL2. This is the default.
        cql2_json: The JSON encoding of CQL2.
    """

    cql2_text = "cql2-text"
    cql2_json = "cql2-json"


class QueryableType(str, Enum):
    """The value types a CQL2 function argument or return value may take."""

    string = "string"
    number = "number"
    integer = "integer"
    datetime = "datetime"
    geometry = "geometry"
    boolean = "boolean"


class Queryable(OGCModel):
    """A single queryable property, expressed as a JSON Schema property.

    A non-spatial queryable declares a ``type``. A spatial queryable instead
    declares a ``format`` such as ``geometry-point`` and omits ``type``
    entirely, which is why ``type`` is optional here.

    Attributes:
        type: The JSON Schema type, for non-spatial queryables.
        format: The format, used for spatial and temporal queryables, for
            example ``geometry-polygon``, ``date-time`` or ``date``.
        title: A human-readable label for the queryable.
        description: A description of the queryable.
        enum: The permitted values, where the queryable is an enumeration.
        x_ogc_role: The role of this queryable, serialised as ``x-ogc-role``;
            for example ``primary-geometry`` or ``primary-instant``.
    """

    type: Optional[str] = Field(
        default=None, description="JSON Schema type; omitted for spatial queryables."
    )
    format: Optional[str] = Field(
        default=None, description="Format, e.g. 'geometry-point' or 'date-time'."
    )
    title: Optional[str] = Field(default=None, description="A label for the queryable.")
    description: Optional[str] = Field(default=None, description="A description of the queryable.")
    enum: Optional[list[Any]] = Field(
        default=None, description="The permitted values, if enumerated."
    )
    x_ogc_role: Optional[str] = Field(
        default=None,
        alias="x-ogc-role",
        description="The role of the queryable, e.g. 'primary-geometry'.",
    )


class Queryables(OGCModel):
    """The queryables resource of a collection, a JSON Schema document.

    Attributes:
        schema_: The JSON Schema dialect, serialised as ``$schema``.
        id: The URI of this resource without query parameters, serialised as
            ``$id``.
        type: The schema type, always ``object``.
        title: A title for the queryables resource.
        description: A description of the queryables resource.
        properties: The queryables, keyed by property name.
        additional_properties: Whether a filter may reference a property that
            is not listed. When true (the default) an unknown reference
            evaluates to null; when false the server returns a 400.
    """

    schema_: str = Field(
        default=QUERYABLES_SCHEMA_DIALECT,
        alias="$schema",
        description="The JSON Schema dialect of this resource.",
    )
    id: Optional[str] = Field(
        default=None,
        alias="$id",
        description="The URI of this resource, without query parameters.",
    )
    type: str = Field(default="object", description="The schema type; always 'object'.")
    title: Optional[str] = Field(default=None, description="A title for the resource.")
    description: Optional[str] = Field(default=None, description="A description of the resource.")
    properties: dict[str, Queryable] = Field(
        default_factory=dict, description="The queryables, keyed by property name."
    )
    additional_properties: bool = Field(
        default=True,
        alias="additionalProperties",
        description="Whether filters may reference unlisted properties.",
    )


class FunctionArgument(OGCModel):
    """An argument of a CQL2 function.

    Attributes:
        type: The value types this argument accepts.
        title: A label for the argument.
        description: A description of the argument.
    """

    type: list[QueryableType] = Field(..., description="The value types this argument accepts.")
    title: Optional[str] = Field(default=None, description="A label for the argument.")
    description: Optional[str] = Field(default=None, description="A description of the argument.")


class Function(OGCModel):
    """A CQL2 function offered by the service.

    Attributes:
        name: The function name. Required.
        returns: The value types the function may return. Required.
        description: A description of the function.
        metadata_url: A URI with further documentation, serialised as
            ``metadataUrl``.
        arguments: The function's arguments, in order.
    """

    name: str = Field(..., description="The function name.")
    returns: list[QueryableType] = Field(
        ..., description="The value types the function may return."
    )
    description: Optional[str] = Field(default=None, description="A description of the function.")
    metadata_url: Optional[str] = Field(
        default=None, description="A URI with further documentation."
    )
    arguments: Optional[list[FunctionArgument]] = Field(
        default=None, description="The function's arguments, in order."
    )


class Functions(OGCModel):
    """The response of the ``/functions`` endpoint.

    Attributes:
        functions: The functions the service offers. Required.
    """

    functions: list[Function] = Field(..., description="The functions the service offers.")


class FilterParameters(OGCModel):
    """The filtering query parameters accepted on an items request.

    Attributes:
        filter: The filter expression, in the language given by ``filter_lang``.
        filter_lang: The language of ``filter``, serialised as ``filter-lang``.
            Defaults to ``cql2-text``.
        filter_crs: The CRS that geometries in ``filter`` are given in,
            serialised as ``filter-crs``.
    """

    filter: Optional[str] = Field(default=None, description="The filter expression.")
    filter_lang: FilterLang = Field(
        default=FilterLang.cql2_text,
        alias="filter-lang",
        description="The language of the filter expression.",
    )
    filter_crs: Optional[str] = Field(
        default=None,
        alias="filter-crs",
        description="The CRS of geometries in the filter expression.",
    )
