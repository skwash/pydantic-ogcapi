"""Landing page, conformance, extent and collection objects.

Reference: OGC 17-069r4, landingPage.yaml / confClasses.yaml / extent.yaml /
collection.yaml / collections.yaml
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field, field_validator

from .._base import OGCModel
from .constants import CRS84, GREGORIAN_TRS, CRS84h
from .link import Link


class LandingPage(OGCModel):
    """The landing page of an OGC API - Features service.

    Attributes:
        links: Links to the API definition, the conformance declaration and
            the collections. Required.
        title: The title of the service.
        description: A description of the service.
    """

    links: list[Link] = Field(..., description="Links to the service's resources.")
    title: Optional[str] = Field(default=None, description="The title of the service.")
    description: Optional[str] = Field(default=None, description="A description of the service.")


class ConformanceDeclaration(OGCModel):
    """The conformance classes a service claims to implement.

    Attributes:
        conforms_to: The conformance class URIs, serialised as ``conformsTo``.
    """

    conforms_to: list[str] = Field(..., description="The conformance class URIs the service implements.")


class SpatialExtent(OGCModel):
    """The spatial extent of the features in a collection.

    Attributes:
        bbox: One or more bounding boxes, each of 4 ordinates (2D) or 6 (3D).
            The first is the overall extent; any others are more precise
            sub-extents.
        crs: The coordinate reference system the bounding boxes are given in.
    """

    bbox: list[list[float]] = Field(..., min_length=1, description="One or more bounding boxes; the first is overall.")
    crs: Literal[CRS84, CRS84h] = Field(default=CRS84, description="The CRS of the bounding boxes.")

    @field_validator("bbox")
    @classmethod
    def _check_bbox_lengths(cls, boxes: list[list[float]]) -> list[list[float]]:
        """Require each bounding box to hold exactly 4 or 6 ordinates."""
        for box in boxes:
            if len(box) not in (4, 6):
                raise ValueError(f"each bbox must have 4 or 6 ordinates, got {len(box)}")
        return boxes


class TemporalExtent(OGCModel):
    """The temporal extent of the features in a collection.

    Attributes:
        interval: One or more intervals, each a two-element ``[start, end]``
            pair in which either end may be null to mean unbounded. The first
            is the overall extent; any others are more precise sub-extents.
        trs: The temporal reference system the intervals are given in.
    """

    interval: list[list[Optional[datetime]]] = Field(
        ..., min_length=1, description="One or more intervals; the first is overall."
    )
    trs: Literal[GREGORIAN_TRS] = Field(default=GREGORIAN_TRS, description="The temporal reference system.")

    @field_validator("interval")
    @classmethod
    def _check_intervals(cls, intervals: list[list[Optional[datetime]]]) -> list[list[Optional[datetime]]]:
        """Require each interval to be exactly two elements, start before end."""
        for entry in intervals:
            if len(entry) != 2:
                raise ValueError(f"each interval must have exactly 2 elements, got {len(entry)}")
            start, end = entry
            if start is not None and end is not None and end < start:
                raise ValueError(f"interval end ({end}) must not precede its start ({start})")
        return intervals


class Extent(OGCModel):
    """The spatial and temporal extent of the features in a collection.

    Attributes:
        spatial: The spatial extent, if known.
        temporal: The temporal extent, if known.
    """

    spatial: Optional[SpatialExtent] = Field(default=None, description="The spatial extent of the collection.")
    temporal: Optional[TemporalExtent] = Field(default=None, description="The temporal extent of the collection.")


class Collection(OGCModel):
    """A collection of features offered by the service.

    Attributes:
        id: The identifier used for this collection in URIs. Required.
        links: Links to the collection's resources, including its items.
        title: A human-readable title for the collection.
        description: A description of the collection.
        extent: The spatial and temporal extent of the collection's features.
        item_type: The type of the items in the collection, serialised as
            ``itemType``. Defaults to ``feature``.
        crs: The coordinate reference systems in which features may be
            requested. Defaults to CRS84 only.
        storage_crs: The CRS the features are stored in (Part 2), serialised
            as ``storageCrs``.
        storage_crs_coordinate_epoch: The coordinate epoch of ``storage_crs``
            as a decimal year (Part 2), serialised as
            ``storageCrsCoordinateEpoch``.
    """

    id: str = Field(..., description="The identifier of the collection.")
    links: list[Link] = Field(..., description="Links to the collection's resources.")
    title: Optional[str] = Field(default=None, description="A title for the collection.")
    description: Optional[str] = Field(default=None, description="A description of the collection.")
    extent: Optional[Extent] = Field(default=None, description="The extent of the collection's features.")
    item_type: str = Field(default="feature", description="The type of the items in the collection.")
    crs: list[str] = Field(
        default_factory=lambda: [CRS84],
        description="The CRSs in which features may be requested.",
    )
    storage_crs: Optional[str] = Field(default=None, description="The CRS the features are stored in (Part 2).")
    storage_crs_coordinate_epoch: Optional[float] = Field(
        default=None,
        description="Coordinate epoch of the storage CRS, as a decimal year (Part 2).",
    )


class Collections(OGCModel):
    """The response of the ``/collections`` endpoint.

    Attributes:
        links: Links to related resources. Required.
        collections: The collections offered by the service. Required.
        crs: A global list of CRS identifiers that a collection's own ``crs``
            may reference with the JSON pointer ``#/crs`` (Part 2).
    """

    links: list[Link] = Field(..., description="Links to related resources.")
    collections: list[Collection] = Field(..., description="The collections offered by the service.")
    crs: Optional[list[str]] = Field(
        default=None,
        description="Global CRS list referenceable as '#/crs' by a collection (Part 2).",
    )
