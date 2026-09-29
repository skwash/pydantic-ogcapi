"""Create, Replace, Update and Delete support.

Part 4 defines no new JSON response bodies: the outcome of a transaction is
carried by the HTTP status code and by headers such as ``Location`` and
``ETag``. These models therefore describe that metadata, so that a client or
server can reason about it in the same typed way as the response bodies.

Reference: OGC 20-002 (OGC API - Features - Part 4: Create, Replace, Update
and Delete), draft.
"""

from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import Field

from .._base import OGCModel


class TransactionStatus(IntEnum):
    """The HTTP status codes a transaction endpoint returns.

    Attributes:
        ok: The request succeeded and the body carries the result.
        created: A feature was created; ``Location`` gives its URI.
        accepted: The request was queued rather than applied immediately.
        no_content: The request succeeded with no response body.
        bad_request: The request was malformed.
        not_found: The feature or collection does not exist.
        conflict: The request conflicts with the current state of the resource.
        precondition_failed: A conditional header did not match.
        precondition_required: The server requires a conditional header.
    """

    ok = 200
    created = 201
    accepted = 202
    no_content = 204
    bad_request = 400
    not_found = 404
    conflict = 409
    precondition_failed = 412
    precondition_required = 428


class TransactionResponse(OGCModel):
    """The outcome of a create, replace, update or delete request.

    Attributes:
        status: The HTTP status code returned.
        location: For a create, the URI of the new feature, from the
            ``Location`` header.
        etag: The entity tag of the resource, from the ``ETag`` header, for
            use in a later ``If-Match``.
        last_modified: When the resource was last modified, from the
            ``Last-Modified`` header, for use in a later
            ``If-Unmodified-Since``.
    """

    status: TransactionStatus = Field(..., description="The HTTP status code returned.")
    location: Optional[str] = Field(
        default=None, description="URI of the created feature, from the Location header."
    )
    etag: Optional[str] = Field(
        default=None, description="Entity tag of the resource, from the ETag header."
    )
    last_modified: Optional[datetime] = Field(
        default=None, description="When the resource was last modified."
    )

    @property
    def is_success(self) -> bool:
        """Whether the status code indicates the transaction succeeded."""
        return self.status < 400


class ConditionalHeaders(OGCModel):
    """The conditional request headers used for optimistic locking.

    A client sends one of these with a replace, update or delete so that the
    request only applies if the feature has not changed since it was read.

    Attributes:
        if_match: An entity tag previously returned in ``ETag``. On a PUT this
            also forces replace-only semantics: the server must not treat the
            request as an insert.
        if_unmodified_since: A timestamp previously returned in
            ``Last-Modified``.
    """

    if_match: Optional[str] = Field(
        default=None,
        alias="If-Match",
        description="Entity tag the resource must still match.",
    )
    if_unmodified_since: Optional[datetime] = Field(
        default=None,
        alias="If-Unmodified-Since",
        description="Timestamp the resource must not have been modified since.",
    )

    def to_headers(self) -> dict[str, str]:
        """Render these as HTTP request headers, omitting those not set."""
        headers: dict[str, str] = {}
        if self.if_match is not None:
            headers["If-Match"] = self.if_match
        if self.if_unmodified_since is not None:
            headers["If-Unmodified-Since"] = self.if_unmodified_since.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
        return headers
