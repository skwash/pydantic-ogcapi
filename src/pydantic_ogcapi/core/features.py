"""OGC API extensions to the RFC 7946 GeoJSON Feature objects.

OGC API - Features returns ordinary GeoJSON, with a small number of additional
members layered on top. These models subclass the ``pydantic_geojson`` models
so that all of the RFC 7946 geometry validation is inherited unchanged.

Reference: OGC 17-069r4, featureGeoJSON.yaml and featureCollectionGeoJSON.yaml
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_geojson import FeatureCollectionModel, FeatureModel

from .link import Link


def _strip_null_altitude(value: Any) -> Any:
    """Drop the trailing null altitude that pydantic-geojson emits for 2D positions.

    ``pydantic_geojson`` models a position as a 3-tuple whose altitude defaults
    to ``None``, so a 2D point serialises as ``[lon, lat, null]``, which is not
    valid GeoJSON. This walks a dumped structure and trims that trailing null
    from any ``coordinates`` member, at any nesting depth.
    """
    if isinstance(value, dict):
        return {
            key: _trim_positions(val) if key == "coordinates" else _strip_null_altitude(val)
            for key, val in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_strip_null_altitude(item) for item in value]
    return value


def _trim_positions(value: Any) -> Any:
    """Recursively trim a trailing ``None`` from each position in a coordinates member."""
    if isinstance(value, (list, tuple)):
        items = list(value)
        # A bare position: numbers, possibly with a trailing None altitude.
        if items and all(item is None or isinstance(item, (int, float)) for item in items):
            while items and items[-1] is None:
                items.pop()
            return items
        return [_trim_positions(item) for item in items]
    return value


class _GeoJSONOGCModel:
    """Mixin applying this package's wire-format conventions to GeoJSON models.

    The GeoJSON models are inherited from ``pydantic_geojson``, so they do not
    pick up :class:`~pydantic_ogcapi._base.OGCModel`. This mixin re-applies the
    same camelCase aliasing and dump defaults on top of the GeoJSON base config.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Dump using wire-format names, omitting members that are not set."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return _strip_null_altitude(super().model_dump(**kwargs))

    def model_dump_json(self, **kwargs: Any) -> str:
        """Serialise to JSON using wire-format names, omitting unset members."""
        import json

        indent = kwargs.pop("indent", None)
        return json.dumps(self.model_dump(**kwargs), default=str, indent=indent)


class Feature(_GeoJSONOGCModel, FeatureModel):
    """A GeoJSON Feature as returned by an OGC API - Features endpoint.

    Extends the RFC 7946 Feature with the links member defined by OGC API.
    The ``id`` and ``geometry`` members are inherited from
    :class:`pydantic_geojson.FeatureModel`.

    Attributes:
        links: Links to related resources, typically including a ``self`` link
            and a ``collection`` link back to the owning collection.
    """

    links: Optional[list[Link]] = Field(
        default=None, description="Links to related resources."
    )


class FeatureCollection(_GeoJSONOGCModel, FeatureCollectionModel):
    """A GeoJSON FeatureCollection as returned by an OGC API - Features endpoint.

    Extends the RFC 7946 FeatureCollection with the paging and provenance
    members defined by OGC API - Features.

    Attributes:
        features: The features in this response. Narrowed from the base model
            so that each entry carries the OGC ``links`` member.
        links: Links to related resources, typically including ``self`` and,
            when the result set is paged, ``next`` and ``prev``.
        time_stamp: When this response was generated, serialised as
            ``timeStamp``.
        number_matched: The total number of features matching the query,
            across all pages. Serialised as ``numberMatched``.
        number_returned: The number of features in this response. Serialised
            as ``numberReturned``.
    """

    features: list[Feature] = Field(
        ..., description="The features in this response."
    )
    links: Optional[list[Link]] = Field(
        default=None, description="Links to related resources."
    )
    time_stamp: Optional[datetime] = Field(
        default=None,
        alias="timeStamp",
        description="When this response was generated.",
    )
    number_matched: Optional[int] = Field(
        default=None,
        alias="numberMatched",
        ge=0,
        description="Total number of features matching the query.",
    )
    number_returned: Optional[int] = Field(
        default=None,
        alias="numberReturned",
        ge=0,
        description="Number of features in this response.",
    )
