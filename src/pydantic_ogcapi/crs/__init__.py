"""Part 2: Coordinate Reference Systems by Reference."""

from ..core.constants import CONF_CRS
from .models import CrsParameters, format_content_crs, parse_content_crs

__all__ = [
    "CONF_CRS",
    "CrsParameters",
    "format_content_crs",
    "parse_content_crs",
]
