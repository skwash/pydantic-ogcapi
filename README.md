# pydantic-ogcapi

[![CI](https://github.com/skwash/pydantic-ogcapi/actions/workflows/ci.yml/badge.svg)](https://github.com/skwash/pydantic-ogcapi/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydantic-ogcapi.svg)](https://pypi.org/project/pydantic-ogcapi/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydantic-ogcapi.svg)](https://pypi.org/project/pydantic-ogcapi/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Pydantic v2 models for the [OGC API - Features](https://ogcapi.ogc.org/features/)
standards, extending [pydantic-geojson](https://pypi.org/project/pydantic-geojson/).

The GeoJSON `Feature` and `FeatureCollection` models subclass their
`pydantic_geojson` counterparts, so all RFC 7946 geometry validation is
inherited unchanged; this package adds the members OGC API layers on top.

## Installation

```bash
pip install pydantic-ogcapi
```

## Usage

Every public name is re-exported from the package root, so a single import is
usually enough:

```python
from pydantic_ogcapi import Collection, FeatureCollection, Link

collection = Collection(
    id="buildings",
    title="Buildings",
    links=[Link(href="/collections/buildings/items", rel="items")],
)
collection.model_dump()
# {'id': 'buildings', 'links': [...], 'title': 'Buildings',
#  'itemType': 'feature', 'crs': ['http://www.opengis.net/def/crs/OGC/1.3/CRS84']}
```

The per-part modules stay importable when that reads more clearly:

```python
from pydantic_ogcapi.core import LandingPage
from pydantic_ogcapi.crs import CrsParameters
from pydantic_ogcapi.filtering import Queryables
from pydantic_ogcapi.transaction import TransactionResponse
```

### Naming

Models declare **snake_case** attributes and serialise to the **camelCase**
(and, for some query parameters, kebab-case) member names the standards
define. Both spellings are accepted when parsing:

```python
fc = FeatureCollection.model_validate({"type": "FeatureCollection", "features": [], "numberMatched": 127})
fc.number_matched  # 127
fc.model_dump()["numberMatched"]  # 127
```

`model_dump()` and `model_dump_json()` default to `by_alias=True` and
`exclude_none=True`, so output carries the wire names and omits members that
were never set — OGC responses distinguish an absent member from a null one.

### Parsing query parameters

```python
from pydantic_ogcapi import BoundingBox, DatetimeInterval

DatetimeInterval.parse("2018-02-12T00:00:00Z/..")  # half-open interval
BoundingBox.parse("-180,-90,180,90")  # 2D bounding box
```

## Layout

| Module | Standard | Contents |
| --- | --- | --- |
| `pydantic_ogcapi.core` | Part 1: Core (17-069r4) | `LandingPage`, `ConformanceDeclaration`, `Collection`, `Collections`, `Extent`, `Feature`, `FeatureCollection`, `Link`, query parameters |
| `pydantic_ogcapi.crs` | Part 2: CRS by Reference (18-058) | `CrsParameters`, `Content-Crs` helpers |
| `pydantic_ogcapi.filtering` | Part 3: Filtering (19-079r2) | `Queryables`, `Functions`, `FilterParameters`, CQL2 constants |
| `pydantic_ogcapi.transaction` | Part 4: CRUD (20-002, draft) | `TransactionResponse`, `ConditionalHeaders`, `TransactionStatus` |

Well-known URIs (`CRS84`, `GREGORIAN_TRS`) and the conformance class URIs
(`CONF_CORE`, `CONF_CRS`, `CONF_FILTER`, …) are exported from the root too.

## Notes on the standards

A few details that are easy to get wrong, and which the models encode:

- The `/collections` response has **no** `timeStamp`/`numberMatched`/`numberReturned`;
  those belong only to the GeoJSON feature collection.
- `Link` in Features Part 1 has no `templated`/`varBase`, and the landing page
  has no `attribution` — those come from OGC API - Common. Extra members are
  allowed and round-trip, so a server that sends them still works.
- The temporal reference system URI lives under `/def/uom/`:
  `http://www.opengis.net/def/uom/ISO-8601/0/Gregorian`.
- A spatial queryable omits `type` and uses `format` instead.
- Part 4 defines no new response bodies; its outcome is the status code plus
  the `Location`, `ETag` and `Last-Modified` headers.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Releasing

The version is single-sourced from `__version__` in
`src/pydantic_ogcapi/__init__.py`; `pyproject.toml` reads it from there.

1. Bump `__version__` and merge that to `main`.
2. Publish a GitHub Release tagged `v<version>` (for example `v0.1.0`).

That triggers the publish workflow, which builds the sdist and wheel,
verifies the tag matches `__version__`, and uploads to PyPI via trusted
publishing. To rehearse first, run the workflow manually from the Actions tab
and choose the `testpypi` target.

Publishing is irreversible — a version number cannot be reused on PyPI even
after a release is deleted — so the workflow never runs on an ordinary push.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
