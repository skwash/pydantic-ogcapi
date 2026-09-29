"""Query parameter models for the /items and /collections endpoints.

These model the request side of OGC API - Features rather than a response
body, so that a server can validate incoming parameters and a client can build
a well-formed request.

Reference: OGC 17-069r4 Section 7.15 (parameters)
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import Field, field_validator

from .._base import OGCModel

#: Sentinel used for the open end of a datetime interval.
OPEN_ENDED = ".."


class DatetimeInterval(OGCModel):
    """A parsed ``datetime`` query parameter.

    The parameter is either a single RFC 3339 instant, or a closed or
    half-open interval written ``start/end`` where either side may be ``..``
    (or empty) to mean unbounded.

    Attributes:
        start: The start of the interval, or None if unbounded.
        end: The end of the interval, or None if unbounded.
        is_instant: True when the parameter was a single instant rather than
            an interval, in which case ``start`` and ``end`` are equal.
    """

    start: Optional[datetime] = Field(default=None, description="Start of the interval, or None if unbounded.")
    end: Optional[datetime] = Field(default=None, description="End of the interval, or None if unbounded.")
    is_instant: bool = Field(default=False, description="Whether the parameter was a single instant.")

    @classmethod
    def parse(cls, value: str) -> "DatetimeInterval":
        """Parse a ``datetime`` query parameter value.

        Args:
            value: The raw parameter, for example ``2018-02-12T23:20:52Z`` or
                ``2018-02-12T00:00:00Z/..``.

        Returns:
            The parsed interval.

        Raises:
            ValueError: If the value is empty, has more than one separator,
                is open at both ends, or has an end before its start.
        """
        raw = value.strip()
        if not raw:
            raise ValueError("datetime parameter must not be empty")

        if "/" not in raw:
            instant = _parse_instant(raw)
            return cls(start=instant, end=instant, is_instant=True)

        parts = raw.split("/")
        if len(parts) != 2:
            raise ValueError(f"datetime interval must have exactly one '/' separator, got {value!r}")

        head, tail = (part.strip() for part in parts)
        start = None if head in ("", OPEN_ENDED) else _parse_instant(head)
        end = None if tail in ("", OPEN_ENDED) else _parse_instant(tail)

        if start is None and end is None:
            raise ValueError("datetime interval must not be open at both ends")
        if start is not None and end is not None and end < start:
            raise ValueError(f"datetime interval end ({tail}) must not precede its start ({head})")
        return cls(start=start, end=end, is_instant=False)

    def to_parameter(self) -> str:
        """Render this interval back to its query parameter form."""
        if self.is_instant and self.start is not None:
            return _format_instant(self.start)
        head = _format_instant(self.start) if self.start else OPEN_ENDED
        tail = _format_instant(self.end) if self.end else OPEN_ENDED
        return f"{head}/{tail}"


def _parse_instant(value: str) -> datetime:
    """Parse a single RFC 3339 instant, accepting a trailing ``Z``."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid RFC 3339 datetime: {value!r}") from exc


def _format_instant(value: datetime) -> str:
    """Render a datetime as an RFC 3339 instant using ``Z`` for UTC."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class BoundingBox(OGCModel):
    """A parsed ``bbox`` query parameter.

    The parameter is 4 numbers for a 2D box (``minx,miny,maxx,maxy``) or 6 for
    a 3D box (``minx,miny,minz,maxx,maxy,maxz``).

    Attributes:
        values: The raw ordinates, either 4 or 6 of them.
    """

    values: list[float] = Field(..., description="The bounding box ordinates: 4 for 2D, 6 for 3D.")

    @field_validator("values")
    @classmethod
    def _check_length(cls, values: list[float]) -> list[float]:
        """Reject a bbox that is not 4 or 6 ordinates long."""
        if len(values) not in (4, 6):
            raise ValueError(f"bbox must have 4 or 6 ordinates, got {len(values)}")
        return values

    @classmethod
    def parse(cls, value: str) -> "BoundingBox":
        """Parse a comma-separated ``bbox`` parameter value."""
        try:
            ordinates = [float(part) for part in value.split(",")]
        except ValueError as exc:
            raise ValueError(f"bbox must be a comma-separated list of numbers: {value!r}") from exc
        return cls(values=ordinates)

    @property
    def is_3d(self) -> bool:
        """Whether this is a 3D (6-ordinate) bounding box."""
        return len(self.values) == 6

    def to_parameter(self) -> str:
        """Render this bounding box back to its query parameter form."""
        return ",".join(_format_number(v) for v in self.values)


def _format_number(value: float) -> str:
    """Render a float without a trailing ``.0`` where it is integral."""
    return str(int(value)) if value == int(value) else str(value)
