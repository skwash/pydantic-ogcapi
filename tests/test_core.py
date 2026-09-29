"""Tests for the Part 1 Core models."""

import pytest
from pydantic import ValidationError

from pydantic_ogcapi import (
    CRS84,
    GREGORIAN_TRS,
    BoundingBox,
    Collection,
    Collections,
    ConformanceDeclaration,
    DatetimeInterval,
    Extent,
    Feature,
    FeatureCollection,
    LandingPage,
    Link,
    OGCException,
    SpatialExtent,
    TemporalExtent,
)


class TestLink:
    def test_requires_href_and_rel(self):
        with pytest.raises(ValidationError):
            Link(href="/x")
        with pytest.raises(ValidationError):
            Link(rel="self")

    def test_dump_omits_unset_members(self):
        assert Link(href="/x", rel="self").model_dump() == {"href": "/x", "rel": "self"}

    def test_extra_members_round_trip(self):
        # templated/varBase come from OGC API - Common, not Features Part 1.
        link = Link.model_validate({"href": "/x", "rel": "self", "templated": True})
        assert link.model_dump()["templated"] is True


class TestLandingPage:
    def test_requires_links(self):
        with pytest.raises(ValidationError):
            LandingPage(title="Service")

    def test_minimal(self):
        page = LandingPage(links=[Link(href="/", rel="self")])
        assert page.model_dump() == {"links": [{"href": "/", "rel": "self"}]}


class TestConformance:
    def test_alias_round_trip(self):
        decl = ConformanceDeclaration.model_validate({"conformsTo": ["http://x/core"]})
        assert decl.conforms_to == ["http://x/core"]
        assert decl.model_dump() == {"conformsTo": ["http://x/core"]}

    def test_accepts_snake_case_input(self):
        decl = ConformanceDeclaration(conforms_to=["http://x/core"])
        assert decl.model_dump() == {"conformsTo": ["http://x/core"]}


class TestExtent:
    def test_spatial_defaults_to_crs84(self):
        assert SpatialExtent(bbox=[[-180, -90, 180, 90]]).crs == CRS84

    def test_spatial_accepts_2d_and_3d(self):
        SpatialExtent(bbox=[[-180, -90, 180, 90]])
        SpatialExtent(bbox=[[-180, -90, 0, 180, 90, 100]])

    @pytest.mark.parametrize("bad", [[[1, 2, 3]], [[1, 2, 3, 4, 5]], [[]]])
    def test_spatial_rejects_wrong_ordinate_count(self, bad):
        with pytest.raises(ValidationError):
            SpatialExtent(bbox=bad)

    def test_spatial_rejects_unknown_crs(self):
        with pytest.raises(ValidationError):
            SpatialExtent(bbox=[[-180, -90, 180, 90]], crs="http://example.com/crs/1")

    def test_spatial_requires_at_least_one_bbox(self):
        with pytest.raises(ValidationError):
            SpatialExtent(bbox=[])

    def test_temporal_defaults_to_gregorian(self):
        extent = TemporalExtent(interval=[["2011-11-11T12:22:11Z", None]])
        assert extent.trs == GREGORIAN_TRS

    def test_temporal_allows_open_ends(self):
        extent = TemporalExtent(interval=[[None, None]])
        assert extent.interval[0] == [None, None]

    def test_temporal_rejects_wrong_length(self):
        with pytest.raises(ValidationError):
            TemporalExtent(interval=[["2011-11-11T12:22:11Z"]])

    def test_temporal_rejects_reversed_interval(self):
        with pytest.raises(ValidationError):
            TemporalExtent(
                interval=[["2020-01-01T00:00:00Z", "2019-01-01T00:00:00Z"]]
            )

    def test_extent_members_optional(self):
        assert Extent().model_dump() == {}


class TestCollection:
    def test_defaults_match_spec(self):
        coll = Collection(id="buildings", links=[Link(href="/c/b", rel="self")])
        assert coll.item_type == "feature"
        assert coll.crs == [CRS84]

    def test_dump_uses_camel_case(self):
        coll = Collection(
            id="b",
            links=[Link(href="/c/b", rel="self")],
            storage_crs=CRS84,
            storage_crs_coordinate_epoch=2017.23,
        )
        dumped = coll.model_dump()
        assert dumped["itemType"] == "feature"
        assert dumped["storageCrs"] == CRS84
        assert dumped["storageCrsCoordinateEpoch"] == 2017.23

    def test_requires_id_and_links(self):
        with pytest.raises(ValidationError):
            Collection(id="b")

    def test_collections_global_crs_is_optional(self):
        resp = Collections(links=[Link(href="/c", rel="self")], collections=[])
        assert "crs" not in resp.model_dump()


class TestFeatures:
    def test_feature_carries_links(self):
        feat = Feature(
            type="Feature",
            geometry={"type": "Point", "coordinates": [1.0, 2.0]},
            id=7,
            links=[Link(href="/items/7", rel="self")],
        )
        assert feat.model_dump()["links"][0]["href"] == "/items/7"

    def test_feature_id_accepts_string_or_int(self):
        assert Feature(type="Feature", geometry=None, id="abc").id == "abc"
        assert Feature(type="Feature", geometry=None, id=5).id == 5

    def test_two_dimensional_position_has_no_null_altitude(self):
        feat = Feature(type="Feature", geometry={"type": "Point", "coordinates": [1.0, 2.0]})
        assert feat.model_dump()["geometry"]["coordinates"] == [1.0, 2.0]

    def test_three_dimensional_position_keeps_altitude(self):
        feat = Feature(
            type="Feature", geometry={"type": "Point", "coordinates": [1.0, 2.0, 30.0]}
        )
        assert feat.model_dump()["geometry"]["coordinates"] == [1.0, 2.0, 30.0]

    def test_nested_polygon_rings_are_trimmed(self):
        feat = Feature(
            type="Feature",
            geometry={"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
        )
        rings = feat.model_dump()["geometry"]["coordinates"]
        assert rings == [[[0, 0], [1, 0], [1, 1], [0, 0]]]

    def test_geometry_validation_is_inherited(self):
        # A linear ring must be closed; pydantic-geojson enforces this.
        with pytest.raises(ValidationError):
            Feature(
                type="Feature",
                geometry={"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1]]]},
            )

    def test_collection_paging_members_use_camel_case(self):
        fc = FeatureCollection(
            type="FeatureCollection",
            features=[],
            number_matched=127,
            number_returned=10,
            time_stamp="2017-08-17T08:05:32Z",
        )
        dumped = fc.model_dump()
        assert dumped["numberMatched"] == 127
        assert dumped["numberReturned"] == 10
        assert "timeStamp" in dumped

    def test_collection_parses_camel_case_input(self):
        fc = FeatureCollection.model_validate(
            {"type": "FeatureCollection", "features": [], "numberMatched": 3}
        )
        assert fc.number_matched == 3

    def test_negative_counts_rejected(self):
        with pytest.raises(ValidationError):
            FeatureCollection(type="FeatureCollection", features=[], number_matched=-1)

    def test_json_round_trip(self):
        fc = FeatureCollection(
            type="FeatureCollection",
            features=[
                Feature(type="Feature", geometry={"type": "Point", "coordinates": [1.0, 2.0]})
            ],
            number_returned=1,
        )
        assert FeatureCollection.model_validate_json(fc.model_dump_json()).number_returned == 1


class TestException:
    def test_requires_code(self):
        with pytest.raises(ValidationError):
            OGCException(description="boom")

    def test_description_optional(self):
        assert OGCException(code="404").model_dump() == {"code": "404"}


class TestDatetimeInterval:
    def test_instant(self):
        parsed = DatetimeInterval.parse("2018-02-12T23:20:52Z")
        assert parsed.is_instant
        assert parsed.start == parsed.end

    def test_bounded_interval(self):
        parsed = DatetimeInterval.parse("2018-02-12T00:00:00Z/2018-03-18T12:31:12Z")
        assert parsed.start is not None and parsed.end is not None

    @pytest.mark.parametrize(
        "value,has_start,has_end",
        [("2018-02-12T00:00:00Z/..", True, False), ("../2018-03-18T12:31:12Z", False, True)],
    )
    def test_half_bounded(self, value, has_start, has_end):
        parsed = DatetimeInterval.parse(value)
        assert (parsed.start is not None) is has_start
        assert (parsed.end is not None) is has_end

    @pytest.mark.parametrize(
        "bad",
        ["", "../..", "a/b/c", "nonsense", "2018-03-18T12:31:12Z/2018-02-12T00:00:00Z"],
    )
    def test_rejects_invalid(self, bad):
        with pytest.raises(ValueError):
            DatetimeInterval.parse(bad)

    @pytest.mark.parametrize(
        "value",
        [
            "2018-02-12T23:20:52Z",
            "2018-02-12T00:00:00Z/2018-03-18T12:31:12Z",
            "2018-02-12T00:00:00Z/..",
            "../2018-03-18T12:31:12Z",
        ],
    )
    def test_round_trips_to_parameter(self, value):
        assert DatetimeInterval.parse(value).to_parameter() == value


class TestBoundingBox:
    def test_parses_2d_and_3d(self):
        assert BoundingBox.parse("-180,-90,180,90").is_3d is False
        assert BoundingBox.parse("-1,-2,0,1,2,10").is_3d is True

    @pytest.mark.parametrize("bad", ["1,2,3", "1,2,3,4,5", "a,b,c,d"])
    def test_rejects_invalid(self, bad):
        with pytest.raises(ValueError):
            BoundingBox.parse(bad)

    def test_round_trips(self):
        assert BoundingBox.parse("-180,-90,180,90").to_parameter() == "-180,-90,180,90"
