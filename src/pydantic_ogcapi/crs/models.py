"""Coordinate Reference Systems by Reference.

Part 2 extends Part 1 rather than adding standalone response objects: the
``storageCrs`` members land on a collection and the global ``crs`` list on the
collections response, both of which are already declared on the Part 1 models.
What remains is the query parameters and the Content-Crs response header.

Reference: OGC 18-058 (OGC API - Features - Part 2: Coordinate Reference
Systems by Reference)
"""

from typing import Optional

from pydantic import Field

from .._base import OGCModel
from ..core.constants import CRS84


class CrsParameters(OGCModel):
    """The CRS query parameters accepted on an items request.

    Attributes:
        crs: The CRS the response geometries should be returned in.
        bbox_crs: The CRS the ``bbox`` parameter is expressed in, serialised
            as ``bbox-crs``.
    """

    crs: Optional[str] = Field(
        default=None, description="The CRS to return response geometries in."
    )
    bbox_crs: Optional[str] = Field(
        default=None,
        alias="bbox-crs",
        description="The CRS the bbox parameter is expressed in.",
    )


def format_content_crs(crs: str = CRS84) -> str:
    """Render a CRS URI for the ``Content-Crs`` response header.

    The header value is the URI enclosed in angle brackets.

    Args:
        crs: The CRS URI. Defaults to CRS84.

    Returns:
        The header value, for example
        ``<http://www.opengis.net/def/crs/OGC/1.3/CRS84>``.
    """
    return f"<{crs}>"


def parse_content_crs(value: str) -> str:
    """Extract the CRS URI from a ``Content-Crs`` header value.

    Args:
        value: The header value, with or without its angle brackets.

    Returns:
        The bare CRS URI.
    """
    return value.strip().lstrip("<").rstrip(">")
