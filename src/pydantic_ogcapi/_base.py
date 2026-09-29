"""Shared base model and conventions for all OGC API model modules.

Every model in this package serialises to the exact member names defined by the
OGC API standards (which are camelCase, and occasionally kebab-case for query
parameters) while exposing idiomatic snake_case attributes in Python.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class OGCModel(BaseModel):
    """Base class for every OGC API object in this package.

    Attributes are declared in snake_case and are automatically given a
    camelCase alias, so ``number_matched`` round-trips as ``numberMatched`` on
    the wire. Both spellings are accepted on input.

    Subclasses that need a member name the generator cannot derive (for example
    the kebab-case ``filter-lang`` query parameter) may set an explicit
    ``alias`` on the field, which takes precedence.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Dump the model using wire-format names and omitting unset members.

        Overrides the pydantic defaults so that ``by_alias`` and
        ``exclude_none`` are on unless the caller says otherwise; OGC responses
        treat an absent member and a null member differently.
        """
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs: Any) -> str:
        """Serialise to JSON using wire-format names and omitting unset members."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump_json(**kwargs)
