"""Link object, shared by every OGC API response.

Reference: OGC 17-069r4 (OGC API - Features - Part 1: Core), link.yaml
"""

from typing import Optional

from pydantic import Field

from .._base import OGCModel


class Link(OGCModel):
    """A web link, as used throughout the OGC API standards.

    Attributes:
        href: The URI of the linked resource. Required.
        rel: The link relation type, for example ``self``, ``alternate``,
            ``next``, ``items`` or ``describedby``.
        type: The media type of the linked resource, for example
            ``application/geo+json``.
        hreflang: The language of the linked resource, as an RFC 5646 tag.
        title: Human-readable label for the link, for use in a user interface.
        length: The expected size of the linked resource, in bytes.

    Note:
        ``templated`` and ``varBase`` are defined by OGC API - Common, not by
        Features Part 1, so they are not declared here. The model allows extra
        members, so a server that sends them will still round-trip them.
    """

    href: str = Field(..., description="The URI of the linked resource.")
    rel: str = Field(..., description="The link relation type.")
    type: Optional[str] = Field(default=None, description="The media type of the linked resource.")
    hreflang: Optional[str] = Field(
        default=None, description="The language of the linked resource (RFC 5646 tag)."
    )
    title: Optional[str] = Field(default=None, description="Human-readable label for the link.")
    length: Optional[int] = Field(
        default=None, description="Expected size of the linked resource, in bytes."
    )
