"""Exception (error) response object.

Reference: OGC 17-069r4, exception.yaml
"""

from typing import Optional

from pydantic import Field

from .._base import OGCModel


class Exception_(OGCModel):
    """An error response returned by an OGC API endpoint.

    Named with a trailing underscore to avoid shadowing the Python builtin;
    it is exported as :class:`OGCException` from the package root.

    Attributes:
        code: A machine-readable error code.
        description: A human-readable explanation of the error.
    """

    code: str = Field(..., description="A machine-readable error code.")
    description: Optional[str] = Field(
        default=None, description="A human-readable explanation of the error."
    )


OGCException = Exception_
